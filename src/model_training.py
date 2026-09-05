# ============================================================
# model_training.py — ML Model Training Pipeline
# ============================================================
#
# YEH FILE KYA KARTI HAI?
# ────────────────────────
# Feature engineering se jo customer_features.csv bana,
# uspe ML model train karta hai.
#
# WORKFLOW (Krish Naik sir wala proper approach):
# ───────────────────────────────────────────────
# 1. Data load karo (customer_features.csv)
# 2. X (features) aur y (label) separate karo
# 3. Train/Test split karo (80/20)
# 4. ColumnTransformer banao:
#    - Numerical columns → SimpleImputer(median) → StandardScaler
#    - Categorical columns → SimpleImputer(most_frequent) → OneHotEncoder
# 5. Multiple models test karo (6 models)
# 6. Sabka score compare karo
# 7. Best model save karo (pickle)
#
# KEY CONCEPTS EXPLAINED:
# ──────────────────────
# SimpleImputer   = Null values ko fill karta hai
#                   (median = beech wali value, most_frequent = sabse common)
# StandardScaler  = Sab numbers ko same scale pe lata hai
#                   (mean=0, std=1 bana deta hai)
# OneHotEncoder   = "Mumbai" → [1,0,0], "Delhi" → [0,1,0]
#                   (ML model text nahi samajhta, numbers chahiye)
# ColumnTransformer = Numerical aur Categorical pe ALAG processing
#                     ek saath handle karta hai
# Pipeline        = Preprocessing + Model ko ek chain mein jodta hai
#                   (data leakage nahi hota, clean code)
# ============================================================

import pandas as pd
import numpy as np
import os
import sys
import pickle   # Model ko file mein save karne ke liye

# ── Sklearn imports (ML library) ──
from sklearn.model_selection import train_test_split  # Data split
from sklearn.preprocessing import StandardScaler      # Number scaling
from sklearn.preprocessing import OneHotEncoder        # Category → numbers
from sklearn.impute import SimpleImputer               # Null filling
from sklearn.compose import ColumnTransformer          # Column-wise processing
from sklearn.pipeline import Pipeline                  # Chain banane ke liye

# ── Models (6 alag models test karenge) ──
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier
)

# ── XGBoost (best model for tabular data) ──
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARNING] XGBoost not installed. Install: pip install xgboost")

# ── Evaluation metrics (model kitna accha hai measure karne ke liye) ──
from sklearn.metrics import (
    accuracy_score,         # Kitne % sahi predict kiye
    precision_score,        # Jitne ko "abusive" bola unme se kitne sach mein the
    recall_score,           # Jo sach mein abusive the unme se kitne pakde
    f1_score,               # Precision aur Recall ka balance
    classification_report,  # Full detailed report
    confusion_matrix        # TP, TN, FP, FN matrix
)

# ── Logger aur Exception ──
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from src.exception import CustomException


def train_model():
    """
    Full ML training pipeline.
    Returns: best model name, best score, trained pipeline
    """
    try:
        logger.info("=" * 50)
        logger.info("MODEL TRAINING STARTED")
        logger.info("=" * 50)

        # ════════════════════════════════════════════════
        # STEP 1: Data load karo
        # ════════════════════════════════════════════════
        
        artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
        data_path = os.path.join(artifacts_dir, "customer_features.csv")
        
        logger.info(f"Loading data from: {data_path}")
        df = pd.read_csv(data_path)
        print(f"\n[1] Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info(f"Data shape: {df.shape}")

        # ════════════════════════════════════════════════
        # STEP 2: X (features) aur y (label) separate karo
        # ════════════════════════════════════════════════
        # X = wo columns jinse model SEEKHEGA (input)
        # y = wo column jo model PREDICT karega (output/answer)
        # customer_id hata do — woh identifier hai, feature nahi
        
        # Columns jo model ke kaam ki NAHI hain
        drop_cols = ["customer_id", "potentially_abusive"]
        
        X = df.drop(columns=drop_cols)   # Features (input)
        y = df["potentially_abusive"]     # Label (output: 0 ya 1)
        
        print(f"[2] X shape: {X.shape}, y shape: {y.shape}")
        print(f"    Label distribution: 0={sum(y==0)}, 1={sum(y==1)}")
        logger.info(f"X shape: {X.shape}, y distribution: {dict(y.value_counts())}")

        # ════════════════════════════════════════════════
        # STEP 3: Numerical aur Categorical columns identify karo
        # ════════════════════════════════════════════════
        # Numerical = numbers wale columns (age, amount, rate)
        # Categorical = text wale columns (city, segment, category)
        # Dono pe ALAG processing hogi
        
        numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
        
        print(f"\n[3] Column types identified:")
        print(f"    Numerical ({len(numerical_cols)}):  {numerical_cols}")
        print(f"    Categorical ({len(categorical_cols)}): {categorical_cols}")
        logger.info(f"Numerical cols: {numerical_cols}")
        logger.info(f"Categorical cols: {categorical_cols}")

        # ════════════════════════════════════════════════
        # STEP 4: Train/Test Split
        # ════════════════════════════════════════════════
        # 80% data se model SEEKHEGA (training)
        # 20% data se model TEST hoga (unseen data)
        #
        # Kyun? — Agar sab data pe train karoge toh model "ratta" maar lega
        # (overfitting). Test data pe check karna zaroori hai ki
        # model NAYE data pe bhi kaam karta hai ya nahi.
        #
        # stratify=y → dono parts mein 0 aur 1 ka ratio same rahega
        # random_state=42 → har baar same split milega (reproducible)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,       # 20% test ke liye
            random_state=42,     # Fixed seed
            stratify=y           # Label ka ratio maintain karo
        )
        
        print(f"\n[4] Train/Test split done:")
        print(f"    Train: {X_train.shape[0]} rows")
        print(f"    Test:  {X_test.shape[0]} rows")
        logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

        # ════════════════════════════════════════════════
        # STEP 5: ColumnTransformer banao (PREPROCESSING)
        # ════════════════════════════════════════════════
        # Yeh Krish Naik sir ka favorite part hai!
        #
        # ColumnTransformer kya karta hai?
        # - Numerical columns pe: Imputer → Scaler
        # - Categorical columns pe: Imputer → Encoder
        # - Sab ek saath, ek object mein!
        #
        # Pipeline kya karta hai?
        # - Steps ko CHAIN mein jodta hai
        # - Data pehle Step 1 se guzarta hai, phir Step 2 se
        
        # Numerical columns ke liye pipeline:
        # Step 1: SimpleImputer(median) → null values ko median se bharo
        #         (median = beech wali value, outliers se affect nahi hoti)
        # Step 2: StandardScaler → sab numbers ko same scale pe lao
        #         (mean=0, std=1 — toh amount=50000 aur age=30 dono comparable)
        num_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        
        # Categorical columns ke liye pipeline:
        # Step 1: SimpleImputer(most_frequent) → null ko sabse common value se bharo
        # Step 2: OneHotEncoder → "Mumbai"→[1,0,0], "Delhi"→[0,1,0]
        #         handle_unknown='ignore' → agar test mein naya city aaye toh error na de
        cat_pipeline = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        
        # ColumnTransformer: dono pipelines ko combine karo
        # "num" pipeline numerical_cols pe chalegi
        # "cat" pipeline categorical_cols pe chalegi
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_pipeline, numerical_cols),
                ("cat", cat_pipeline, categorical_cols)
            ],
            remainder="drop"  # Baaki columns drop karo
        )
        
        print(f"\n[5] Preprocessing pipeline created:")
        print(f"    Numerical:  SimpleImputer(median) -> StandardScaler")
        print(f"    Categorical: SimpleImputer(mode) -> OneHotEncoder")
        logger.info("Preprocessing pipeline created")

        # ════════════════════════════════════════════════
        # STEP 6: Multiple Models define karo
        # ════════════════════════════════════════════════
        # Hum 6 alag models test karenge — dekhenge kaunsa BEST perform karta hai
        #
        # LogisticRegression — Simple, fast, baseline model
        # DecisionTree       — Ek tree banata hai (if-else jaisa)
        # RandomForest       — Bahut saare trees (voting karke decide)
        # GradientBoosting   — Trees ek ke baad ek, pichli galti sudharta hai
        # XGBoost            — GradientBoosting ka advanced version (king of tabular)
        # AdaBoost           — Weak models ko combine karta hai
        
        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
            "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=42, algorithm="SAMME"),
        }
        
        # XGBoost add karo agar installed hai
        if XGBOOST_AVAILABLE:
            models["XGBoost"] = XGBClassifier(
                n_estimators=100, random_state=42, eval_metric="logloss",
                use_label_encoder=False
            )
        
        print(f"\n[6] Models to test: {list(models.keys())}")
        logger.info(f"Models: {list(models.keys())}")

        # ════════════════════════════════════════════════
        # STEP 7: Har model ko train aur test karo
        # ════════════════════════════════════════════════
        # Har model ke liye:
        #   1. Pipeline banao (preprocessor + model)
        #   2. Training data pe fit karo (seekho)
        #   3. Test data pe predict karo (output nikalo)
        #   4. Score calculate karo (kitna sahi nikla)
        
        print(f"\n[7] Training and evaluating models...")
        print(f"{'='*65}")
        print(f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
        print(f"{'='*65}")
        
        results = {}
        best_score = 0
        best_model_name = ""
        best_pipeline = None
        
        for name, model in models.items():
            logger.info(f"Training: {name}")
            
            # Pipeline = preprocessor + model ko ek chain mein jodo
            # Jab fit() call hoga toh:
            #   1. Pehle preprocessor data ko transform karega
            #   2. Phir transformed data model ko jayega
            pipeline = Pipeline(steps=[
                ("preprocessor", preprocessor),
                ("model", model)
            ])
            
            # FIT = model ko training data se SEEKHNE do
            # Yeh step mein model patterns discover karta hai
            pipeline.fit(X_train, y_train)
            
            # PREDICT = test data pe prediction nikalo
            # Model ne jo seekha hai uske basis pe output dega
            y_pred = pipeline.predict(X_test)
            
            # SCORES calculate karo
            acc = accuracy_score(y_test, y_pred)        # Overall kitne % sahi
            prec = precision_score(y_test, y_pred)      # Precision
            rec = recall_score(y_test, y_pred)           # Recall
            f1 = f1_score(y_test, y_pred)                # F1 (balance of prec+rec)
            
            results[name] = {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "pipeline": pipeline
            }
            
            print(f"{name:<25} {acc:>10.4f} {prec:>10.4f} {rec:>10.4f} {f1:>10.4f}")
            logger.info(f"{name}: acc={acc:.4f}, prec={prec:.4f}, rec={rec:.4f}, f1={f1:.4f}")
            
            # Best model track karo (F1 score se compare — kyunki imbalanced data hai)
            if f1 > best_score:
                best_score = f1
                best_model_name = name
                best_pipeline = pipeline
        
        print(f"{'='*65}")
        print(f"\n>>> BEST MODEL: {best_model_name} (F1 Score: {best_score:.4f}) <<<")
        logger.info(f"BEST MODEL: {best_model_name} with F1={best_score:.4f}")

        # ════════════════════════════════════════════════
        # STEP 8: Best model ka detailed report
        # ════════════════════════════════════════════════
        # Classification Report:
        #   - Precision: Jitne ko "1" bola unme se kitne sach mein 1 the
        #   - Recall: Jo sach mein 1 the unme se kitne pakde
        #   - F1: Dono ka harmonic mean (balance)
        #
        # Confusion Matrix:
        #   [[TN, FP],    TN = sahi se "normal" bola
        #    [FN, TP]]    TP = sahi se "abusive" bola
        #                 FP = galat se "abusive" bola (false alarm)
        #                 FN = abusive tha lekin miss kar diya (dangerous!)
        
        print(f"\n{'='*50}")
        print(f"DETAILED REPORT: {best_model_name}")
        print(f"{'='*50}")
        
        y_pred_best = best_pipeline.predict(X_test)
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_best,
                                     target_names=["Normal", "Potentially Abusive"]))
        
        cm = confusion_matrix(y_test, y_pred_best)
        print(f"Confusion Matrix:")
        print(f"                  Predicted Normal  Predicted Abusive")
        print(f"  Actual Normal       {cm[0][0]:>6}            {cm[0][1]:>6}")
        print(f"  Actual Abusive      {cm[1][0]:>6}            {cm[1][1]:>6}")
        
        logger.info(f"Confusion Matrix: {cm.tolist()}")

        # ════════════════════════════════════════════════
        # STEP 9: Best model aur preprocessor SAVE karo
        # ════════════════════════════════════════════════
        # pickle.dump = Python object ko file mein save karna
        # Baad mein pickle.load se wapas load kar sakte ho
        # (FastAPI mein yahi model load karke predictions denge)
        
        model_path = os.path.join(artifacts_dir, "model.pkl")
        preprocessor_path = os.path.join(artifacts_dir, "preprocessor.pkl")
        
        # Full pipeline save karo (preprocessor + model dono ek saath)
        with open(model_path, "wb") as f:
            pickle.dump(best_pipeline, f)
        
        # Preprocessor alag se bhi save karo (debugging ke liye useful)
        with open(preprocessor_path, "wb") as f:
            pickle.dump(preprocessor, f)
        
        print(f"\n[8] Model saved: {model_path}")
        print(f"    Preprocessor saved: {preprocessor_path}")
        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Preprocessor saved to: {preprocessor_path}")
        
        # ════════════════════════════════════════════════
        # STEP 10: Summary save karo
        # ════════════════════════════════════════════════
        
        results_df = pd.DataFrame({
            name: {k: v for k, v in vals.items() if k != "pipeline"}
            for name, vals in results.items()
        }).T
        results_df.to_csv(os.path.join(artifacts_dir, "model_comparison.csv"))
        
        print(f"\n[OK] Model Training Complete!")
        print(f"     Best Model: {best_model_name}")
        print(f"     F1 Score:   {best_score:.4f}")
        print(f"     All results saved to: artifacts/model_comparison.csv")
        
        logger.info("MODEL TRAINING COMPLETED SUCCESSFULLY")
        
        return best_model_name, best_score, best_pipeline
        
    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        raise CustomException(e, sys)


# ── Directly run karo toh yeh chalega ──
if __name__ == "__main__":
    train_model()
