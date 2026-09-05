# backend/services/risk_service.py
# ============================================================
# RISK SERVICE — Wraps ml/predict.py for Backend Use
# ============================================================
# Backend ke routes is service ko call karte hain.
# Yeh service:
#   1. ML feature engineering (ml/feature_engineering.py) call karta hai
#   2. XGBoost + SHAP prediction (ml/predict.py) call karta hai
#   3. Clean response dict return karta hai
# ============================================================

import os
import sys
import json
import uuid
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.feature_engineering import build_features_for_return, _load_data
from ml.predict import get_predictor
from src.logger import logger


def score_return_request(customer_id: str, return_id: str) -> dict:
    """
    Ek return request ka complete risk analysis karo.

    Args:
        customer_id: e.g. "CUST00001"
        return_id:   e.g. "RET000001"

    Returns:
        dict with:
          - return_id, customer_id, order_id
          - risk_score (0-100)
          - risk_level (LOW/MEDIUM/HIGH)
          - action (APPROVE/VERIFY/MANUAL_REVIEW)
          - recommendation (human text)
          - top_risk_factors (SHAP list)
          - feature_snapshot (all 23 feature values)
          - case_id (UUID for investigation tracking)
          - scored_at (timestamp)
    """
    try:
        # Step 1: Load data (cached after first call)
        data = _load_data()

        # Step 2: Validate that return_id and customer_id exist
        returns_df = data["returns"]
        match = returns_df[returns_df["return_id"] == return_id]
        if match.empty:
            raise ValueError(f"Return ID '{return_id}' not found in database.")
        ret_row = match.iloc[0]
        if str(ret_row["customer_id"]) != str(customer_id):
            raise ValueError(
                f"Return '{return_id}' does not belong to customer '{customer_id}'."
            )
        order_id = str(ret_row["order_id"])

        # Step 3: Build the 23-feature vector
        features = build_features_for_return(customer_id, return_id, data)

        # Step 4: ML Prediction + SHAP
        predictor = get_predictor()
        result = predictor.predict_risk(features)

        # Step 5: Assemble final response
        case_id = f"CASE-{uuid.uuid4().hex[:10].upper()}"
        return {
            "case_id": case_id,
            "return_id": return_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "action": result["action"],
            "recommendation": result["recommendation"],
            "top_risk_factors": result["top_risk_factors"],
            "feature_snapshot": result["feature_snapshot"],
            "prediction": result["prediction"],
            "prediction_label": result["prediction_label"],
            "scored_at": datetime.utcnow().isoformat(),
        }

    except ValueError as e:
        logger.warning(f"risk_service validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"risk_service unexpected error: {e}")
        raise


def get_model_metrics() -> dict:
    """
    artifacts/metrics.json se actual model metrics return karo.
    """
    metrics_path = os.path.join(PROJECT_ROOT, "artifacts", "metrics.json")
    if not os.path.exists(metrics_path):
        raise FileNotFoundError("metrics.json not found. Run ml/train.py first.")
    with open(metrics_path) as f:
        return json.load(f)


def get_threshold_analysis() -> list:
    """
    artifacts/threshold_analysis.json se threshold curve data return karo.
    """
    path = os.path.join(PROJECT_ROOT, "artifacts", "threshold_analysis.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)
