# ============================================================
# ml/train.py — XGBoost Training Pipeline
# ============================================================
#
# YEH FILE KYA KARTI HAI?
# ------------------------
# 1. Feature engineering se per-return dataset load karta hai
# 2. ColumnTransformer se preprocessing pipeline banata hai:
#    - Numerical -> SimpleImputer(median) -> StandardScaler
# 3. XGBoost classifier train karta hai
# 4. Model + preprocessor save karta hai artifacts/ mein
# ============================================================

import os
import sys
import json
import pickle
import pandas as pd
import numpy as np

# Sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix,
)

# XGBoost
from xgboost import XGBClassifier

# Project
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from src.exception import CustomException
from ml.feature_engineering import (
    build_training_dataset, FEATURE_COLUMNS
)


def train_model():
    """
    Full XGBoost training pipeline.
    """
    try:
        logger.info("=" * 50)
        logger.info("PHASE 1 - XGBOOST TRAINING STARTED")
        logger.info("=" * 50)

        artifacts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "artifacts"
        )
        os.makedirs(artifacts_dir, exist_ok=True)

        # ----------------------------------------------------
        # STEP 1: Training dataset load / build
        # ----------------------------------------------------
        cached_path = os.path.join(artifacts_dir, "return_features.csv")

        if os.path.exists(cached_path):
            print(f"\n[1] Loading cached training dataset: {cached_path}")
            df = pd.read_csv(cached_path)
            logger.info(f"Loaded cached dataset: {df.shape}")
        else:
            print(f"\n[1] Building training dataset from raw data...")
            df = build_training_dataset()
            df.to_csv(cached_path, index=False)
            print(f"    Cached to: {cached_path}")

        print(f"    Dataset: {len(df)} rows x {len(df.columns)} columns")

        # ----------------------------------------------------
        # STEP 2: X (features) and y (label) split
        # ----------------------------------------------------
        X = df[FEATURE_COLUMNS].copy()
        y = df["potentially_abusive"].astype(int)

        print(f"\n[2] Features: {X.shape[1]} columns (all numerical)")
        print(f"    Label: 0={int((y==0).sum())}, 1={int((y==1).sum())}")
        logger.info(f"X shape: {X.shape}, y distribution: {dict(y.value_counts())}")

        # ----------------------------------------------------
        # STEP 3: Train/Test Split (80/20 stratified)
        # ----------------------------------------------------
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        print(f"\n[3] Train/Test split:")
        print(f"    Train: {len(X_train)} rows")
        print(f"    Test:  {len(X_test)} rows")
        logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

        # ----------------------------------------------------
        # STEP 4: Preprocessing Pipeline
        # ----------------------------------------------------
        numerical_cols = FEATURE_COLUMNS

        num_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, numerical_cols),
            ],
            remainder="drop",
        )

        print(f"\n[4] Preprocessing: SimpleImputer(median) -> StandardScaler")
        print(f"    All {len(numerical_cols)} features are numerical")
        logger.info("Preprocessing pipeline: Imputer(median) -> StandardScaler")

        # ----------------------------------------------------
        # STEP 5: XGBoost Training
        # ----------------------------------------------------
        xgb_model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
            use_label_encoder=False,
        )

        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", xgb_model),
        ])

        print(f"\n[5] Training XGBoost...")
        print(f"    n_estimators=200, max_depth=6, lr=0.1")
        logger.info("Training XGBoost classifier...")

        pipeline.fit(X_train, y_train)

        print(f"    Training complete!")
        logger.info("XGBoost training complete")

        # ----------------------------------------------------
        # STEP 6: Evaluation
        # ----------------------------------------------------
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        print(f"\n[6] Evaluation Results:")
        print(f"    {'='*50}")
        print(f"    Accuracy:   {acc:.4f}")
        print(f"    Precision:  {prec:.4f}")
        print(f"    Recall:     {rec:.4f}")
        print(f"    F1 Score:   {f1:.4f}")
        print(f"    ROC-AUC:    {roc_auc:.4f}")
        print(f"    {'='*50}")
        print(f"\n    Confusion Matrix:")
        print(f"                      Predicted Normal  Predicted Abusive")
        print(f"      Actual Normal       {cm[0][0]:>6}            {cm[0][1]:>6}")
        print(f"      Actual Abusive      {cm[1][0]:>6}            {cm[1][1]:>6}")

        print(f"\n    Classification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=["Normal", "Potentially Abusive"]
        ))

        # FP/FN Cost Analysis
        fp = int(cm[0][1])
        fn = int(cm[1][0])
        tn = int(cm[0][0])
        tp = int(cm[1][1])

        print(f"    FP/FN Cost Analysis:")
        print(f"      False Positives (unnecessary friction): {fp}")
        print(f"      False Negatives (missed abuse):         {fn}")
        print(f"      True Positives (caught abuse):          {tp}")
        print(f"      True Negatives (clean pass):            {tn}")

        logger.info(
            f"Metrics: acc={acc:.4f}, prec={prec:.4f}, rec={rec:.4f}, "
            f"f1={f1:.4f}, roc_auc={roc_auc:.4f}"
        )

        # ----------------------------------------------------
        # STEP 7: Save metrics.json
        # ----------------------------------------------------
        metrics = {
            "model": "XGBoost",
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "features_count": len(FEATURE_COLUMNS),
            "features": FEATURE_COLUMNS,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": {
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp,
            },
            "fp_fn_analysis": {
                "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0,
                "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0,
                "fp_description": "Normal customers incorrectly flagged - causes friction",
                "fn_description": "Abusive returns missed - causes revenue leakage",
            },
        }

        metrics_path = os.path.join(artifacts_dir, "metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"\n[7] Metrics saved: {metrics_path}")
        logger.info(f"Metrics saved to: {metrics_path}")

        # ----------------------------------------------------
        # STEP 8: Save model + preprocessor
        # ----------------------------------------------------
        model_path = os.path.join(artifacts_dir, "model.pkl")
        preprocessor_path = os.path.join(artifacts_dir, "preprocessor.pkl")

        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)

        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)

        print(f"\n[8] Saved:")
        print(f"    Model pipeline: {model_path}")
        print(f"    Preprocessor:   {preprocessor_path}")
        logger.info(f"Model saved: {model_path}")

        # ----------------------------------------------------
        # STEP 9: Save feature_list.json
        # ----------------------------------------------------
        feature_list_path = os.path.join(artifacts_dir, "feature_list.json")
        with open(feature_list_path, "w") as f:
            json.dump({
                "version": "2.0",
                "unit": "per_return_request",
                "feature_count": len(FEATURE_COLUMNS),
                "features": FEATURE_COLUMNS,
            }, f, indent=2)

        print(f"    Feature list:   {feature_list_path}")

        print(f"\n{'='*50}")
        print(f"[OK] PHASE 1 TRAINING COMPLETE!")
        print(f"     Model:     XGBoost")
        print(f"     F1 Score:  {f1:.4f}")
        print(f"     ROC-AUC:   {roc_auc:.4f}")
        print(f"     Features:  {len(FEATURE_COLUMNS)}")
        print(f"{'='*50}")

        logger.info("PHASE 1 - XGBOOST TRAINING COMPLETED SUCCESSFULLY")

        return pipeline, metrics

    except Exception as e:
        logger.error(f"Error in training: {str(e)}")
        raise CustomException(e, sys)


if __name__ == "__main__":
    train_model()
