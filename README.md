# 🛡️ ReturnShield AI — E-Commerce Return & Refund Abuse Guardrail

> **Razorpay Hackathon Edition** &bull; Production-grade AI Microservice and Real-time Merchant Dashboard detecting abusive return behavior, wardrobing, and refund fraud with **97.4% accuracy** and **0.9326 F1-Score**.

---

## 📌 Problem Statement

Indian e-commerce merchants lose over **₹ 10,000+ Crores annually** due to return and refund abuse:
1. **Wardrobing**: Customers purchasing luxury/party apparel, using it once for photos/events, and returning it within 30 days.
2. **Device & Account Farms**: Fraud syndicates creating dozens of burner accounts on the same phone/address to exploit 1st-time user discounts and free returns.
3. **Empty Box & Disproportionate Claims**: Claiming missing items or demanding refunds while keeping the merchandise.

**ReturnShield AI** solves this by analyzing 19 multi-dimensional behavioral signals and applying a production-grade machine learning ensemble to instantly score risk (<15ms) and recommend automated merchant policies.

---

## 🏗️ Architecture & Industry Patterns (Krish Naik Style)

```text
e:\Rozarpay_hecathon\
│
├── artifacts/                  # Saved ML models, preprocessor pipelines & CSVs
│   ├── model.pkl               # Production XGBoost pipeline
│   ├── preprocessor.pkl        # ColumnTransformer (SimpleImputer + Encoders + Scalers)
│   ├── customer_features.csv   # 5,000 processed customer behavioral profiles
│   └── model_comparison.csv    # Benchmark metrics across 6 algorithms
│
├── backend/                    # FastAPI Microservice
│   ├── main.py                 # REST API endpoints, CORS, Swagger Docs
│   ├── schemas.py              # Pydantic data schemas & request validation
│   ├── predictor.py            # Singleton inference engine & explainability rules
│   ├── requirements.txt        # Backend dependencies
│   └── README.md               # Backend documentation & sample cURL calls
│
├── frontend/                   # Modern Glassmorphic Dashboard
│   ├── index.html              # Semantic HTML5 Single-Page Dashboard
│   ├── styles.css              # Custom Vanilla CSS tokens, animations & dark mode
│   ├── app.js                  # Chart.js visualizations, live simulator & audit table
│   └── README.md               # Frontend features & launch guide
│
├── data/                       # Raw synthetic data foundation & generation
│   ├── generate_dataset.py     # Reproducible synthetic dataset generator
│   ├── customers.csv           # 5,000 raw customer records
│   ├── orders.csv              # 34,809 order transactions
│   ├── returns.csv             # 5,998 return requests
│   ├── refunds.csv             # 4,127 refund settlements
│   ├── devices.csv             # 4,598 hardware fingerprint bindings
│   └── addresses.csv           # 4,666 delivery address bindings
│
├── src/                        # Modular ML Engineering Pipeline
│   ├── logger.py               # Timestamped logging utility
│   ├── exception.py            # Custom exception wrapper (file name, line number)
│   ├── feature_engineering.py  # Aggregates 6 CSVs into 19 behavioral features
│   └── model_training.py       # Preprocessor + 6-model training & benchmark
│
├── requirements.txt            # Complete project requirements
├── setup.py                    # Package configuration
└── README.md                   # Project overview & quickstart
```

---

## 🏆 Model Benchmarking & Results

We benchmarked **6 algorithms** on an 80/20 train/test split (4,000 train / 1,000 unseen test) with stratified sampling:

| Algorithm | Accuracy | Precision | Recall | F1 Score | Status |
|---|---|---|---|---|---|
| **XGBoost (Extreme Gradient Boosting)** | **97.40%** | **97.30%** | **89.55%** | **0.9326** | 👑 **Production Champion** |
| GradientBoostingClassifier | 97.10% | 97.25% | 88.06% | 0.9243 | Benchmark Runner-up |
| RandomForestClassifier | 96.20% | 94.54% | 86.07% | 0.9010 | High Stability |
| LogisticRegression (Baseline) | 95.10% | 95.24% | 79.60% | 0.8672 | Linear Baseline |
| AdaBoostClassifier | 94.70% | 90.66% | 82.09% | 0.8616 | Adaptive Boosting |
| DecisionTreeClassifier | 93.40% | 84.97% | 81.59% | 0.8325 | Single Tree |

### Why XGBoost Won:
1. **High Precision (97.3%)**: Essential for consumer trust. Legitimate shoppers rarely get falsely flagged.
2. **High Recall (89.55%)**: Successfully caught 180 out of 201 actual abusive return events in the test dataset.

---

## ⚡ Quickstart: How to Run the Project

### Step 1: Conda Environment Setup
```bash
# Environment create karo
conda create -n returnshield python=3.11 -y

# Activate karo
conda activate returnshield

# Install packages
pip install -r requirements.txt
```

### Step 2: Start Backend (FastAPI Microservice)
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 3: Start Frontend (React Dashboard)
```bash
cd frontend
npm run dev
```
- Open Browser: [http://localhost:3000](http://localhost:3000)

### Step 3b: Production Build (serves via FastAPI at port 8000)
```bash
cd frontend
npm run build
# Then start backend — it will serve frontend/dist automatically
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Dashboard at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API Docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🎯 Key Capabilities & Policy Actions

- **Instant 1-Click Refund**: If Risk Score `< 35%` (Legitimate VIP shopper).
- **Mandatory 3PL Barcode Scan**: If Risk Score `35% - 70%` (Moderate return frequency).
- **Physical Hub Inspection & COD Restriction**: If Risk Score `>= 70%` (Wardrober or device-linked fraud syndicate).

---

## 👨‍💻 Tech Stack
- **Language**: Python 3.11, JavaScript (ES6+), HTML5, CSS3
- **ML Frameworks**: Scikit-Learn, XGBoost, Pandas, NumPy
- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Glassmorphic Vanilla CSS, Chart.js, SVG Radial Gauges
