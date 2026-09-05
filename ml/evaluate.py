# ============================================================
# ml/evaluate.py — Comprehensive Model Evaluation
# ============================================================
#
# YEH FILE KYA KARTI HAI?
# ────────────────────────
# 1. Trained XGBoost model + test dataset load karta hai
# 2. Comprehensive evaluation metrics compute karta hai:
#    - Accuracy, Precision, Recall, F1-Score
#    - ROC-AUC, PR-AUC
#    - Confusion Matrix (TP, TN, FP, FN)
#    - FP/FN Financial / Friction Cost Analysis
#    - Optimal Threshold Analysis (0.1 to 0.9)
# 3. artifacts/metrics.json aur artifacts/threshold_analysis.json save karta hai
# ============================================================

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, precision_recall_curve, roc_curve
)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from src.exception import CustomException
from ml.feature_engineering import FEATURE_COLUMNS, build_training_dataset


def evaluate_model(artifacts_dir: str = None):
    """
    Evaluates the trained model on test data and produces detailed metrics.
    """
    try:
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")

        model_path = os.path.join(artifacts_dir, "model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run ml/train.py first.")

        with open(model_path, "rb") as f:
            pipeline = pickle.load(f)

        data_path = os.path.join(artifacts_dir, "return_features.csv")
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
        else:
            df = build_training_dataset()

        X = df[FEATURE_COLUMNS]
        y = df["potentially_abusive"].astype(int)

        # Use same random state split for testing
        from sklearn.model_selection import train_test_split
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_proba))
        pr_auc = float(average_precision_score(y_test, y_proba))
        cm = confusion_matrix(y_test, y_pred)

        tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

        # Threshold analysis
        threshold_results = []
        for t in np.arange(0.1, 0.95, 0.05):
            t_thresh = round(float(t), 2)
            preds_t = (y_proba >= t_thresh).astype(int)
            cm_t = confusion_matrix(y_test, preds_t)
            tn_t, fp_t, fn_t, tp_t = int(cm_t[0, 0]), int(cm_t[0, 1]), int(cm_t[1, 0]), int(cm_t[1, 1])
            threshold_results.append({
                "threshold": t_thresh,
                "precision": round(float(precision_score(y_test, preds_t, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, preds_t, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, preds_t, zero_division=0)), 4),
                "false_positives": fp_t,
                "false_negatives": fn_t,
                "true_positives": tp_t,
                "true_negatives": tn_t
            })

        metrics = {
            "model": "XGBoost",
            "evaluation_dataset_size": len(X_test),
            "features_count": len(FEATURE_COLUMNS),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": {
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp
            },
            "fp_fn_analysis": {
                "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0,
                "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0,
                "fp_cost_impact": "Customer friction on genuine returns",
                "fn_cost_impact": "Direct financial leakage from missed fraudulent returns"
            }
        }

        metrics_file = os.path.join(artifacts_dir, "metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        thresh_file = os.path.join(artifacts_dir, "threshold_analysis.json")
        with open(thresh_file, "w") as f:
            json.dump(threshold_results, f, indent=2)

        print(f"\n================ MODEL EVALUATION SUMMARY ================")
        print(f"Accuracy:   {acc:.4f}")
        print(f"Precision:  {prec:.4f}")
        print(f"Recall:     {rec:.4f}")
        print(f"F1-Score:   {f1:.4f}")
        print(f"ROC-AUC:    {roc_auc:.4f}")
        print(f"PR-AUC:     {pr_auc:.4f}")
        print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
        print(f"Metrics saved to: {metrics_file}")
        print(f"Threshold curve saved to: {thresh_file}")
        print(f"==========================================================\n")

        return metrics

    except Exception as e:
        logger.error(f"Error in evaluate_model: {e}")
        raise CustomException(e, sys)


if __name__ == "__main__":
    evaluate_model()
