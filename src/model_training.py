# ============================================================
# model_training.py — ML Model Training Pipeline
# ============================================================
# Benchmarks multiple classification algorithms (LogisticRegression,
# DecisionTree, RandomForest, GradientBoosting, AdaBoost, XGBoost),
# evaluates with Stratified K-Fold / Train-Test Split, and persists
# the best model pipeline and preprocessor to artifacts/.
# ============================================================

import os
import sys
import pickle
import pandas as pd
import numpy as np

# Sklearn ML utilities
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Model implementations
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
)

# XGBoost Classifier
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# Model evaluation metrics
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# Logging and error handling
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from src.exception import CustomException


def train_model():
    """
    Executes complete ML training and benchmarking pipeline.
    Returns: best_model_name, best_score, best_pipeline
    """
    try:
        logger.info("=" * 50)
        logger.info("MODEL TRAINING PIPELINE STARTED")
        logger.info("=" * 50)

        # ----------------------------------------------------
        # STEP 1: Load training dataset
        # ----------------------------------------------------
        artifacts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "artifacts"
        )
        data_path = os.path.join(artifacts_dir, "customer_features.csv")

        if not os.path.exists(data_path):
            # Fallback to return_features.csv if customer_features not generated
            data_path = os.path.join(artifacts_dir, "return_features.csv")

        logger.info(f"Loading feature dataset from: {data_path}")
        df = pd.read_csv(data_path)
        print(f"\n[1] Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"Data shape: {df.shape}")

        # ----------------------------------------------------
        # STEP 2: Separate Features (X) and Target Label (y)
        # ----------------------------------------------------
        target_col = "potentially_abusive" if "potentially_abusive" in df.columns else "is_fraudulent"
        drop_cols = [c for c in ["customer_id", "return_id", "order_id", "created_at", "return_date", target_col] if c in df.columns]

        X = df.drop(columns=drop_cols)
        y = df[target_col]

        print(f"[2] Features shape: {X.shape}, Target shape: {y.shape}")
        logger.info(f"X shape: {X.shape}, y distribution: {dict(y.value_counts())}")

        # ----------------------------------------------------
        # STEP 3: Identify Numerical and Categorical Columns
        # ----------------------------------------------------
        numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

        print(f"\n[3] Identified feature columns:")
        print(f"    Numerical ({len(numerical_cols)}):   {numerical_cols[:5]}...")
        print(f"    Categorical ({len(categorical_cols)}): {categorical_cols}")

        # ----------------------------------------------------
        # STEP 4: Stratified Train-Test Split (80/20)
        # ----------------------------------------------------
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        print(f"\n[4] Train/Test Split completed:")
        print(f"    Train: {X_train.shape[0]} samples")
        print(f"    Test:  {X_test.shape[0]} samples")
        logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

        # ----------------------------------------------------
        # STEP 5: Construct ColumnTransformer Preprocessing Pipeline
        # ----------------------------------------------------
        num_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        cat_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, numerical_cols),
                ("cat", cat_pipeline, categorical_cols),
            ],
            remainder="drop",
        )

        print(f"\n[5] Preprocessing pipeline configured successfully.")

        # ----------------------------------------------------
        # STEP 6: Define Candidate Models for Benchmarking
        # ----------------------------------------------------
        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=42, algorithm="SAMME"),
        }

        if XGBOOST_AVAILABLE:
            models["XGBoost"] = XGBClassifier(
                n_estimators=100,
                random_state=42,
                eval_metric="logloss",
                use_label_encoder=False,
            )

        # ----------------------------------------------------
        # STEP 7: Train and Evaluate All Candidates
        # ----------------------------------------------------
        print(f"\n[6] Benchmarking models...")
        print(f"{'='*65}")
        print(f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
        print(f"{'='*65}")

        results = {}
        best_score = 0
        best_model_name = ""
        best_pipeline = None

        for name, model in models.items():
            pipeline = Pipeline(steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            results[name] = {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "pipeline": pipeline,
            }

            print(f"{name:<25} {acc:>10.4f} {prec:>10.4f} {rec:>10.4f} {f1:>10.4f}")
            logger.info(f"{name}: acc={acc:.4f}, prec={prec:.4f}, rec={rec:.4f}, f1={f1:.4f}")

            if f1 > best_score:
                best_score = f1
                best_model_name = name
                best_pipeline = pipeline

        print(f"{'='*65}")
        print(f"\n>>> BEST MODEL SELECTED: {best_model_name} (F1 Score: {best_score:.4f}) <<<")
        logger.info(f"BEST MODEL: {best_model_name} with F1={best_score:.4f}")

        # ----------------------------------------------------
        # STEP 8: Detailed Evaluation Report
        # ----------------------------------------------------
        y_pred_best = best_pipeline.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_best, target_names=["Legitimate", "Abusive/Fraudulent"]))

        cm = confusion_matrix(y_test, y_pred_best)
        print(f"Confusion Matrix:")
        print(f"                  Predicted Normal  Predicted Fraud")
        print(f"  Actual Normal       {cm[0][0]:>6}            {cm[0][1]:>6}")
        print(f"  Actual Fraud        {cm[1][0]:>6}            {cm[1][1]:>6}")

        # ----------------------------------------------------
        # STEP 9: Persist Model Pipeline & Preprocessor Artifacts
        # ----------------------------------------------------
        os.makedirs(artifacts_dir, exist_ok=True)
        model_path = os.path.join(artifacts_dir, "model.pkl")
        preprocessor_path = os.path.join(artifacts_dir, "preprocessor.pkl")

        with open(model_path, "wb") as f:
            pickle.dump(best_pipeline, f)

        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)

        print(f"\n[OK] Model Pipeline saved to: {model_path}")
        print(f"     Preprocessor saved to:   {preprocessor_path}")
        logger.info("MODEL TRAINING COMPLETED SUCCESSFULLY")

        return best_model_name, best_score, best_pipeline

    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        raise CustomException(e, sys)


if __name__ == "__main__":
    train_model()
