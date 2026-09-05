# ReturnShield AI — Complete Project Workflow

## What happens after each merchant action?

---

## Full End-to-End Flow

```
Customer submits return
        │
        ▼
POST /api/risk/score
        │
        ├─ 1. Validate return_id + customer_id exist in DB
        ├─ 2. Build 23 behavioral features (feature_engineering.py)
        ├─ 3. XGBoost pipeline → risk_score (0–100%)
        ├─ 4. SHAP TreeExplainer → top 7 risk factors
        ├─ 5. Decision engine → risk_level + action
        ├─ 6. Save Investigation case (status: PENDING)
        └─ 7. Write RISK_SCORED to audit_log
                │
                ▼
        Groq AI summary generated
        (POST /api/investigations/{case_id}/ai-summary)
                │
                ▼
        Merchant sees dashboard
                │
        ┌───────┴──────────────────────────┐
        │                                  │
    ✅ Approve           🟡 Verify OTP    🔴 Escalate
        │                     │                │
        ▼                     ▼                ▼
POST /api/returns/{id}/approve  /verify  /manual-review
        │
        ├─ Find investigation case by return_id
        ├─ Update action_taken = APPROVE/VERIFY/MANUAL_REVIEW
        ├─ Save merchant notes
        └─ Write action to audit_log (immutable)
```

---

## After "Approve Refund" — What Exactly Happens?

1. `POST /api/returns/{return_id}/approve` is called
2. Backend finds the `Investigation` case for that return
3. Updates the case:
   - `action_taken` → `"APPROVE"`
   - `action_by`    → `"merchant_ops"`
   - `action_notes` → your notes
   - `updated_at`   → current timestamp
4. Writes an immutable `AuditLog` entry:
   - `action = "APPROVE"`
   - `performed_by = "merchant_ops"`
   - `details = notes`
5. Returns the updated case
6. Frontend shows a green toast: "APPROVE recorded"
7. Audit Vault tab updates with the new entry

---

## After "Verify OTP" — What Happens?

Same flow but `action_taken = "VERIFY"`.  
Meaning: customer must provide OTP + courier barcode scan before refund is processed.

---

## After "Escalate to Fraud" — What Happens?

Same flow but `action_taken = "MANUAL_REVIEW"`.  
Meaning: case is escalated to human fraud team. COD restriction may be applied.

---

## How to Check the Full Workflow is Working

### Step 1 — Start backend
```bash
cd e:\Rozarpay_hecathon
.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 2 — Start frontend
```bash
cd e:\Rozarpay_hecathon\frontend
npm run dev
# → http://localhost:3000
```

### Step 3 — Manual verification checklist

| What to check | Where | Expected result |
|---|---|---|
| Backend health | http://127.0.0.1:8000/api/health | `{"status":"healthy","model_loaded":true}` |
| Score a return | POST /api/risk/score | Returns risk_score, risk_level, SHAP factors |
| Dashboard KPIs | http://localhost:3000 (Overview tab) | Total returns, abuse rate, savings |
| Returns queue | Returns Queue tab | List of returns with risk badges |
| AI Simulator | AI Simulator tab | Score + Groq narrative for any preset |
| Approve action | Click ✅ in any return row | Green toast, Audit Vault updates |
| Audit trail | Audit Vault tab | APPROVE/VERIFY/MANUAL_REVIEW entries visible |
| API docs | http://127.0.0.1:8000/docs | Full Swagger UI |

### Step 4 — Full system test
```bash
cd e:\Rozarpay_hecathon
.venv\Scripts\activate
python test_full_system.py
```
Expected output: `🎉 ALL 5 LAYERS VERIFIED SUCCESSFULLY!`

---

## Workflow State Machine

```
Return Created
     │
     ▼
  PENDING  ◄── (auto-set when risk scoring happens)
     │
     ├──→ APPROVE        (low risk, instant refund)
     ├──→ VERIFY         (medium risk, OTP required)
     └──→ MANUAL_REVIEW  (high risk, fraud team)
```

Each state transition is:
- Recorded in `investigations` table
- Written to `audit_logs` table (immutable)
- Visible in Audit Vault tab
