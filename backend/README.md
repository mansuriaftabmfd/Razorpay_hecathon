# 🛡️ ReturnShield AI — Backend Microservice

ReturnShield AI ka backend ek high-performance, asynchronous REST API microservice hai jise **FastAPI** aur **Uvicorn** par banaya gaya hai. Yeh e-commerce merchants ko real-time me abusive return aur refund requests identify karne me madad karta hai.

---

## 📁 Folder Structure

```text
backend/
├── main.py              # FastAPI app instance, CORS middleware, aur API routes
├── schemas.py           # Pydantic models (data validation & schemas)
├── predictor.py         # ML model pipeline loader (artifacts/model.pkl) & inference logic
├── requirements.txt     # Backend-specific dependencies
└── README.md            # Yeh documentation file
```

---

## ⚙️ Setup & Installation

### 1. Conda Environment Activate Karo
```bash
conda activate returnshield
```

### 2. Dependencies Install Karo (agar already nahi hain)
```bash
pip install -r backend/requirements.txt
```

### 3. Server Start Karo
```bash
# Project root (e:\Rozarpay_hecathon) se run karein:
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Server start hone ke baad terminal me dikhega:
`INFO: Uvicorn running on http://127.0.0.1:8000`

---

## 📖 Interactive API Documentation (Swagger UI)

FastAPI automatically interactive documentation generate karta hai:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status aur endpoint directory |
| `GET` | `/api/health` | Service aur model health check |
| `POST` | `/api/predict` | Single customer ki live risk prediction aur explainability |
| `POST` | `/api/batch-predict` | Bulk customers ka risk evaluation aur summary |
| `GET` | `/api/model-stats` | 6 models (XGBoost, RF, GB, etc.) ke benchmark scores |
| `GET` | `/api/sample-customers` | Frontend testing ke liye 15 real customer profiles |

---

## 🧪 Testing with cURL / JSON

### 1. Single Customer Prediction (`POST /api/predict`)

```bash
curl -X POST "http://127.0.0.1:8000/api/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_id": "CUST_TEST_001",
       "account_age_days": 45,
       "city": "Mumbai",
       "customer_segment": "occasional",
       "total_orders": 12,
       "avg_order_amount": 3500.0,
       "total_order_amount": 42000.0,
       "most_common_category": "Clothing",
       "most_common_payment": "COD",
       "total_returns": 8.0,
       "avg_return_amount": 3200.0,
       "total_return_amount": 25600.0,
       "avg_days_to_return": 22.0,
       "total_refunds": 7.0,
       "total_refund_amount": 22400.0,
       "device_linked_accounts": 4,
       "address_linked_accounts": 3,
       "return_rate": 0.67,
       "refund_rate": 0.58,
       "refund_to_order_ratio": 0.53
     }'
```

#### Sample Response:
```json
{
  "customer_id": "CUST_TEST_001",
  "prediction": 1,
  "prediction_label": "Potentially Abusive",
  "risk_score": 96.42,
  "risk_category": "HIGH",
  "recommended_action": "RESTRICT: Require unboxing video, physical hub inspection, and COD deposit on future orders.",
  "top_risk_factors": [
    "Elevated Return Frequency: 67.0% of orders returned",
    "Device Farm Fingerprint: 4 accounts detected on same device",
    "Address Clustering: 3 separate accounts sharing delivery location",
    "High Refund Drain: 53.0% of total order value refunded",
    "Wardrobing Signature: Average return after 22 days of delivery"
  ]
}
```

---

## 🧠 ML Inference Workflow (Krish Naik Style)

1. Request aane par `Pydantic` schema automatically data types validate karta hai.
2. `predictor.py` me singleton `ReturnShieldPredictor` memory me pehle se loaded `artifacts/model.pkl` pipeline ko call karta hai.
3. Pipeline input dataframe par:
   - **ColumnTransformer** se missing values impute karta hai aur categorical strings ko One-Hot encode karta hai.
   - **XGBoost Classifier** se probability estimate nikalta hai.
4. Model output ke basis par calibrated `risk_score` (0-100), automated merchant actionable advisory aur explainability bullet points generate karke instant JSON return karta hai (<15ms response time).
