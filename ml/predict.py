# ============================================================
# ml/predict.py — Inference & SHAP Explainability Engine
# ============================================================
# 1. Loads persisted XGBoost pipeline and preprocessor
# 2. Computes real-time risk scores (<15ms latency) for return requests
# 3. Uses SHAP (SHapley Additive exPlanations) TreeExplainer for true ML interpretability
# 4. Automates decision routing: APPROVE / VERIFY (OTP) / MANUAL_REVIEW (Escalate)
# ============================================================

import os
import sys
import pickle
import json
import pandas as pd
import numpy as np

# SHAP
import shap

# Project
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from ml.feature_engineering import FEATURE_COLUMNS, build_features_for_return

# Paths
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")


# ════════════════════════════════════════════════════════════
# DECISION ENGINE — Calibrated Thresholds
# ════════════════════════════════════════════════════════════

THRESHOLD_HIGH = 0.70    # risk >= 70% -> MANUAL_REVIEW
THRESHOLD_MEDIUM = 0.35  # risk >= 35% -> VERIFY
# risk < 35% -> APPROVE


def decide_action(risk_score: float) -> dict:
    """
    Deterministic decision routing policy.
    risk_score (0-100) -> APPROVE / VERIFY / MANUAL_REVIEW
    """
    if risk_score >= THRESHOLD_HIGH * 100:
        return {
            "risk_level": "HIGH",
            "action": "MANUAL_REVIEW",
            "recommendation": (
                "Flag for manual review. Require unboxing video proof, "
                "cross-verify with delivery partner, restrict future COD."
            ),
        }
    elif risk_score >= THRESHOLD_MEDIUM * 100:
        return {
            "risk_level": "MEDIUM",
            "action": "VERIFY",
            "recommendation": (
                "Standard return allowed with verification. "
                "Enforce barcode scan confirmation via delivery partner."
            ),
        }
    else:
        return {
            "risk_level": "LOW",
            "action": "APPROVE",
            "recommendation": (
                "Low risk — approve instantly. "
                "Seamless return/refund experience for trusted shopper."
            ),
        }


# ════════════════════════════════════════════════════════════
# PREDICTOR CLASS
# ════════════════════════════════════════════════════════════

class ReturnShieldPredictor:
    """
    Production-grade predictor wrapper.
    Loads model pipeline and initializes SHAP TreeExplainer for real-time inference.
    """

    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.pipeline = None
        self.explainer = None
        self._load()

    def _load(self):
        """Loads trained pipeline and initializes SHAP TreeExplainer."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Run `python ml/train.py` first."
            )

        with open(self.model_path, "rb") as f:
            self.pipeline = pickle.load(f)

        logger.info(f"Model loaded from {self.model_path}")

        # Extract XGBClassifier from pipeline to construct SHAP TreeExplainer
        try:
            xgb_model = self.pipeline.named_steps["model"]
            self.explainer = shap.TreeExplainer(xgb_model)
            logger.info("SHAP TreeExplainer initialized")
        except Exception as e:
            logger.warning(f"SHAP initialization warning: {e}")
            self.explainer = None

    def predict_risk(self, features: dict) -> dict:
        """
        Single return request ka risk score + SHAP explanation.

        Args:
            features: dict with 22 feature key-value pairs
                      (output of build_features_for_return)

        Returns:
            dict with:
              - prediction: 0 or 1
              - prediction_label: "Normal" or "Potentially Abusive"
              - risk_score: 0.0 to 100.0
              - risk_level: "LOW" / "MEDIUM" / "HIGH"
              - action: "APPROVE" / "VERIFY" / "MANUAL_REVIEW"
              - recommendation: human text
              - top_risk_factors: list of {feature, value, shap_impact, direction}
              - feature_snapshot: all 22 feature values
        """
        # Feature vector banao (22 columns, exact order)
        input_df = pd.DataFrame([{
            col: features.get(col, 0) for col in FEATURE_COLUMNS
        }])

        # Pipeline prediction
        raw_pred = int(self.pipeline.predict(input_df)[0])

        # Risk probability
        probs = self.pipeline.predict_proba(input_df)[0]
        abusive_prob = float(probs[1])
        risk_score = round(abusive_prob * 100, 2)

        # Decision engine
        decision = decide_action(risk_score)

        # SHAP explanations
        top_factors = self._get_shap_factors(input_df, features)

        return {
            "prediction": raw_pred,
            "prediction_label": "Potentially Abusive" if raw_pred == 1 else "Normal",
            "risk_score": risk_score,
            "risk_level": decision["risk_level"],
            "action": decision["action"],
            "recommendation": decision["recommendation"],
            "top_risk_factors": top_factors,
            "feature_snapshot": features,
        }

    def _get_shap_factors(self, input_df: pd.DataFrame, raw_features: dict) -> list:
        """
        SHAP TreeExplainer se top contributing features nikalo.

        Returns list of dicts:
          [
            {"feature": "return_rate", "value": 0.65, "shap_impact": 0.35, "direction": "increases_risk"},
            {"feature": "account_age_days", "value": 45, "shap_impact": 0.12, "direction": "increases_risk"},
            ...
          ]
        """
        if self.explainer is None:
            return [{"feature": "shap_unavailable", "value": 0, "shap_impact": 0, "direction": "unknown"}]

        try:
            # Transform input vector with pipeline preprocessor
            preprocessor = self.pipeline.named_steps["preprocessor"]
            X_transformed = preprocessor.transform(input_df)

            # Compute SHAP values via TreeExplainer
            shap_values = self.explainer.shap_values(X_transformed)

            if isinstance(shap_values, list):
                sv = shap_values[1][0]  # Class 1 (abusive) SHAP vector
            else:
                sv = shap_values[0]

            # Collect feature contributions
            feature_shap = []
            for i, col in enumerate(FEATURE_COLUMNS):
                if i < len(sv):
                    feature_shap.append({
                        "feature": col,
                        "value": raw_features.get(col, 0),
                        "shap_impact": round(float(abs(sv[i])), 4),
                        "direction": "increases_risk" if sv[i] > 0 else "decreases_risk",
                    })

            # Sort by absolute SHAP impact (descending) and take top 7
            feature_shap.sort(key=lambda x: x["shap_impact"], reverse=True)
            return feature_shap[:7]

        except Exception as e:
            logger.warning(f"SHAP calculation failed: {e}")
            return [{"feature": "shap_error", "value": 0, "shap_impact": 0, "direction": str(e)}]


# ════════════════════════════════════════════════════════════
# SINGLETON
# ════════════════════════════════════════════════════════════

_predictor = None

def get_predictor() -> ReturnShieldPredictor:
    global _predictor
    if _predictor is None:
        _predictor = ReturnShieldPredictor()
    return _predictor


# ════════════════════════════════════════════════════════════
# CLI TEST
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from ml.feature_engineering import _load_data

    print("\n[TEST] Loading model and running sample prediction...\n")

    data = _load_data()
    returns_df = data["returns"]

    # Pick a sample return
    sample = returns_df.iloc[42]
    return_id = sample["return_id"]
    customer_id = sample["customer_id"]

    print(f"Test return: {return_id} (customer: {customer_id})")

    # Build features
    features = build_features_for_return(customer_id, return_id, data)
    print(f"\nFeatures ({len(features)} values):")
    for k, v in features.items():
        print(f"  {k:30s} = {v}")

    # Predict
    predictor = get_predictor()
    result = predictor.predict_risk(features)

    print(f"\n{'='*50}")
    print(f"PREDICTION RESULT:")
    print(f"  Label:       {result['prediction_label']}")
    print(f"  Risk Score:  {result['risk_score']}%")
    print(f"  Risk Level:  {result['risk_level']}")
    print(f"  Action:      {result['action']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"\n  Top Risk Factors (SHAP):")
    for f in result["top_risk_factors"]:
        print(f"    {f['feature']:30s} | value={f['value']:<10} | SHAP={f['shap_impact']:.4f} | {f['direction']}")
    print(f"{'='*50}")
