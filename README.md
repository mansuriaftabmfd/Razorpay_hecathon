# 🛡️ ReturnShield AI — Real-Time E-Commerce Return Abuse & Fraud Detection Engine

[![Track](https://img.shields.io/badge/Razorpay%20Hackathon%202026-Track%202%3A%20AI%20Risk%20Manager-blue.svg)](https://github.com/mansuriaftabmfd/Razorpay_hecathon)
[![Latency](https://img.shields.io/badge/Inference%20Latency-%3C15ms-brightgreen.svg)]()
[![Model](https://img.shields.io/badge/ML%20Engine-XGBoost%20%2B%20SHAP-orange.svg)]()
[![Accuracy](https://img.shields.io/badge/Accuracy-96.8%25-teal.svg)]()
[![ROC-AUC](https://img.shields.io/badge/ROC--AUC-0.985-purple.svg)]()

---

## 📌 Executive Summary

In Indian e-commerce, returns and refunds represent an annual loss exceeding **₹10,000+ Crores**. Merchants struggle to differentiate between genuine shoppers seeking replacements and organized abuse rings engaging in:
- **Wardrobing / Rental Abuse**: Purchasing high-value apparel or electronics, using them temporarily, and exploiting liberal return windows.
- **Empty Box / Item Swap Fraud**: Returning soap bars or fake substitutes instead of authentic high-ticket products.
- **Device & Address Farming**: Creating multiple synthetic accounts from a single device or address cluster to cycle through signup discounts and first-return policies.
- **Velocity Surges**: Placing bursts of orders and filing simultaneous return claims across multiple orders before flags are raised.

**ReturnShield AI** is an enterprise-grade, real-time risk intelligence platform built for **Razorpay Merchants**. It evaluates return requests at the point of initiation in **under 15 milliseconds**, assigns a calibrated risk score (0–100%), provides **game-theoretic SHAP explainability** for every decision, and automates resolution into **Instant Refund (Approve)**, **OTP/Barcode Gate (Verify)**, or **Fraud Escalation (Manual Review)**.

---

## 🏗️ System Architecture

```
                                  ┌─────────────────────────────────────────┐
                                  │      Razorpay Merchant Dashboard        │
                                  │   (React 19 + Vite + Modern Sidebar)    │
                                  └────────────────────┬────────────────────┘
                                                       │  HTTP / REST API
                                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FastAPI High-Performance Async Backend                                 │
├────────────────────────────────┬───────────────────────────────────────┬────────────────────────────────┤
│       Risk Scoring Service     │          Case Investigation           │      Immutable Audit Vault     │
│   (/api/risk/score, /returns)  │   (Groq LLaMA-3 Narrative Analysis)   │   (Tamper-Proof Action Ledger) │
└────────────────┬───────────────┴───────────────────┬───────────────────┴────────────────┬───────────────┘
                 │                                   │                                    │
                 ▼                                   ▼                                    ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│     Feature Engineering (23D)   │ │       XGBoost ML Pipeline       │ │       SQLite / PostgreSQL       │
│  Zero Data-Leakage Aggregates   │ │  SHAP TreeExplainer & Calibrated│ │  Customers, Orders, Returns,    │
│  Velocity & Farming Signals     │ │  Decision Thresholds (<15ms)   │ │  Refunds, Devices, Audit Logs   │
└─────────────────────────────────┘ └─────────────────────────────────┘ └─────────────────────────────────┘
```

---

## 🔬 23-Dimensional Behavioral Feature Engineering

ReturnShield builds a rich feature vector strictly preserving **temporal integrity** (no data leakage — only records timestamped prior to the return event are used):

### 1. Historical Customer Aggregates (8 Signals)
| # | Feature Name | Data Type | Risk Indicator & Behavior Analyzed |
|---|---|---|---|
| 1 | `account_age_days` | `int` | Days since account creation; young accounts (<120 days) with rapid return volume signal disposable accounts. |
| 2 | `previous_orders` | `int` | Total historical order count serving as baseline context. |
| 3 | `previous_returns` | `int` | Cumulative return count across customer lifespan. |
| 4 | `return_rate` | `float` | `previous_returns / previous_orders`. Values exceeding 0.35 indicate abnormal return frequency. |
| 5 | `previous_refund_count` | `int` | Total successful refunds processed. |
| 6 | `previous_refund_amount` | `float` | Cumulative monetary value (₹) drained from the merchant via refunds. |
| 7 | `average_order_value` | `float` | Historical mean order value (AOV) for anomaly comparison. |
| 8 | `refund_to_order_ratio` | `float` | Cumulative refund sum / cumulative order sum; ratios > 0.30 reflect net revenue leakage. |

### 2. Velocity & Burst Signals (4 Signals)
| # | Feature Name | Data Type | Risk Indicator & Behavior Analyzed |
|---|---|---|---|
| 9 | `orders_last_24h` | `int` | Sudden order spikes immediately preceding return filings. |
| 10 | `returns_last_7d` | `int` | Rapid short-term return filings (≥3 returns/week indicates velocity abuse). |
| 11 | `returns_last_30d` | `int` | Medium-term return acceleration. |
| 12 | `refunds_last_30d` | `int` | Monthly refund velocity drain. |

### 3. Current Transaction Context (4 Signals)
| # | Feature Name | Data Type | Risk Indicator & Behavior Analyzed |
|---|---|---|---|
| 13 | `current_order_amount` | `float` | Total monetary value (₹) of the order undergoing return. |
| 14 | `current_return_amount`| `float` | Monetary value claimed for return/refund. |
| 15 | `return_to_order_ratio`| `float` | Claim amount relative to order price; flags partial vs. full refund exploits. |
| 16 | `days_to_return` | `int` | Interval between delivery/order and return request (<2 days or >20 days indicate wardrobing/tampering). |

### 4. Advanced Behavioral Patterns (5 Signals)
| # | Feature Name | Data Type | Risk Indicator & Behavior Analyzed |
|---|---|---|---|
| 17 | `same_reason_count` | `int` | Frequency of repeated return excuses (e.g. repeated "item defective" or "empty package"). |
| 18 | `unique_return_reasons`| `int` | Breadth of distinct return excuses cited across history. |
| 19 | `return_frequency` | `float` | Normalized monthly return tempo (`returns / (account_age / 30)`). |
| 20 | `return_gap_days` | `int` | Days elapsed since customer's previous return filing. |
| 21 | `high_value_return_flag`| `int (0/1)`| Flagged `1` if current return value > 2× customer historical AOV. |

### 5. Multi-Accounting & Device Farming (2 Signals)
| # | Feature Name | Data Type | Risk Indicator & Behavior Analyzed |
|---|---|---|---|
| 22 | `device_linked_accounts` | `int` | Number of distinct customer accounts mapped to the identical hardware device ID (>3 indicates device farming). |
| 23 | `address_linked_accounts`| `int` | Number of distinct customer accounts mapped to the identical delivery address. |

---

## 📊 Machine Learning Model & Benchmark Results

We benchmarked 6 candidate classification architectures on stratified 80/20 train-test splits:

```
=================================================================
Model                       Accuracy  Precision     Recall         F1
=================================================================
LogisticRegression            0.8920     0.8410     0.8120     0.8260
DecisionTree                  0.9140     0.8650     0.8520     0.8580
RandomForest                  0.9540     0.9380     0.9160     0.9270
AdaBoost                      0.9310     0.8940     0.8870     0.8900
GradientBoosting              0.9580     0.9450     0.9280     0.9360
XGBoost (Production Champion) 0.9680     0.9620     0.9480     0.9550
=================================================================
```

### Production Model Metrics:
- **Accuracy**: `96.8%`
- **Precision**: `96.2%` (Minimizes false accusations and customer friction)
- **Recall**: `94.8%` (Catches 95 out of 100 fraudulent return attempts)
- **F1 Score**: `0.955`
- **ROC-AUC Score**: `0.985`
- **Inference Latency**: `<15ms` per single-item scoring request

---

## ⚙️ Decision Engine & Policy Automation

| Risk Tier | Score Range | Automated Advisory | Merchant Action & Friction Gate |
|---|---|---|---|
| 🟢 **LOW RISK** | `0.0% – 29.9%` | **Auto-Approve** | Instant UPI/Source refund issued immediately. Maximum customer delight. |
| 🟡 **MEDIUM RISK**| `30.0% – 69.9%` | **Verify OTP** | Gate refund behind OTP verification and courier item barcode verification before payout. |
| 🔴 **HIGH RISK** | `70.0% – 100.0%`| **Manual Escalation**| Quarantine refund, alert internal fraud ops, require warehouse physical inspection. |

---

## 🖥️ Modern Web Dashboard Experience

The frontend is built with **React 19**, **Vite**, and a custom dark/teal design system inspired by top-tier modern fintech interfaces:
1. **Vertical Sidebar Navigation**:
   - Collapsible desktop sidebar (260px expanded ↔ 78px compact icon dock).
   - Off-canvas drawer with smooth backdrop blur on mobile and tablet devices.
   - Live AI Model Heartbeat indicator with pulse animation.
2. **Dashboard Overview**: KPI metric cards (Total Cases, Abuse Rate, Financial Loss Prevented, Live Throughput), return velocity breakdown charts, and real-time risk distribution.
3. **Returns Queue**: Interactive queue with instant inline approval, OTP request, and fraud escalation actions.
4. **AI Simulator**: Interactive sandbox to test custom behavioral profiles and preview real-time XGBoost scores, SHAP contribution waterfalls, and Groq LLaMA-3 analytical summaries.
5. **ML Model Metrics**: Live confusion matrices, ROC-AUC curves, PR-curves, and feature importance rankings.
6. **Immutable Audit Vault**: Full-width compliance ledger recording every scoring event and merchant override.

---

## 🔌 API Endpoint Directory

### Risk Scoring
- `POST /api/risk/score`: Scores a single return request (`customer_id`, `return_id`) and returns calibrated risk score, recommendation, and SHAP factors.
- `POST /api/predict`: Direct inference on raw customer behavioral parameters.
- `POST /api/batch-predict`: High-throughput batch scoring for bulk return queues.

### Return & Case Management
- `GET /api/returns`: Lists all return requests with attached risk scores and status.
- `GET /api/investigations`: Lists all generated risk investigation cases.
- `GET /api/investigations/{case_id}`: Retrieves comprehensive case file with SHAP factors and AI summary.
- `POST /api/investigations/{case_id}/ai-summary`: Generates/retrieves Groq LLaMA-3 explanatory narrative.
- `POST /api/returns/{return_id}/approve`: Approves return refund and records immutable audit log.
- `POST /api/returns/{return_id}/verify`: Triggers OTP verification workflow.
- `POST /api/returns/{return_id}/manual-review`: Escalates return to specialized fraud team.

### System & Audit
- `GET /api/health`: Health status of API, database connectivity, and loaded ML model.
- `GET /api/overview`: Summary dashboard metrics for merchant overview.
- `GET /api/model/metrics`: Model validation scores, confusion matrix, and ROC-AUC.
- `GET /api/model/thresholds`: Threshold sensitivity sweep curve.
- `GET /api/audit-logs`: Retrieves immutable compliance ledger of all operator actions.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+ (or Python 3.11 / 3.13)
- **Node.js**: 18+ and `npm`

### Option 1: One-Click Startup Script
```powershell
# In project root:
.\run.ps1
# or
.\run.bat
```

### Option 2: Manual Startup

#### 1. Backend Setup
```bash
# Navigate to project root
cd e:\Rozarpay_hecathon

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Set your Groq API key in .env for LLM summaries
cp .env.example .env

# Seed database from synthetic data
python backend/seed_data.py

# Launch FastAPI backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
*API Docs available at: `http://127.0.0.1:8000/docs`*

#### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend
cd e:\Rozarpay_hecathon\frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*Dashboard available at: `http://127.0.0.1:3000/`*

---

## 🧪 Comprehensive Verification Suite

To verify all 5 architectural layers (Data, ML Model, Feature Engine, Database, and FastAPI Services):
```bash
python test_full_system.py
```
**Expected Result**: `🎉 ALL 5 LAYERS VERIFIED SUCCESSFULLY!`

---

## 👥 Razorpay Hackathon 2026 Submission

- **Track**: Track 2: AI Risk Manager
- **Repository**: [https://github.com/mansuriaftabmfd/Razorpay_hecathon.git](https://github.com/mansuriaftabmfd/Razorpay_hecathon.git)
- **License**: MIT
