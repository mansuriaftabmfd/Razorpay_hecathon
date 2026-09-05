# ============================================================
# backend/services/risk_service.py — Risk Scoring Service
# ============================================================
# Bridges backend API routes with ML feature engineering and
# XGBoost/SHAP prediction pipelines.
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
    Executes end-to-end risk evaluation for a given return request.

    Args:
        customer_id: Customer identifier, e.g. "CUST00001"
        return_id: Return request identifier, e.g. "RET000001"

    Returns:
        Structured response dictionary with calibrated risk score,
        decision category, SHAP explainability factors, and feature snapshot.
    """
    try:
        # Step 1: Access indexed datasets
        data = _load_data()

        # Step 2: Validate customer and return existence
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

        # Step 3: Compute 23-dimensional feature vector without data leakage
        features = build_features_for_return(customer_id, return_id, data)

        # Step 4: Execute model inference + SHAP TreeExplainer
        predictor = get_predictor()
        result = predictor.predict_risk(features)

        # Step 5: Format response payload with generated case ID
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
        logger.warning(f"Risk service validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Risk service unexpected error: {e}")
        raise


def get_model_metrics() -> dict:
    """
    Reads verified model performance metrics from artifacts/metrics.json.
    """
    metrics_path = os.path.join(PROJECT_ROOT, "artifacts", "metrics.json")
    if not os.path.exists(metrics_path):
        raise FileNotFoundError("metrics.json not found. Train model first.")
    with open(metrics_path) as f:
        return json.load(f)


def get_threshold_analysis() -> list:
    """
    Retrieves decision threshold sensitivity sweep from artifacts.
    """
    path = os.path.join(PROJECT_ROOT, "artifacts", "threshold_analysis.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)
