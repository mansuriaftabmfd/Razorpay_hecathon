# backend/main.py
# ============================================================
# RETURNSHIELD AI — FastAPI Backend (Phase 2)
# ============================================================
# All endpoints per the 3-Phase specification.
# Uses SQLite database (seeded from CSVs).
# ============================================================

import os
import sys
import json
import uuid
from typing import Optional

# Load .env file for GROQ_API_KEY and other secrets
from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db, create_tables
from backend import models
from backend.schemas import (
    RiskScoreRequest, RiskScoreResponse,
    ActionRequest, ActionResponse,
    InvestigationOut, AISummaryResponse,
    CustomerOut, ReturnOut, OrderOut,
    DashboardOverview, ModelMetricsResponse, HealthResponse,
)
from backend.services import risk_service, investigation_service
from src.logger import logger

# ── App init ──────────────────────────────────────────────────────
app = FastAPI(
    title="ReturnShield AI",
    description=(
        "Merchant-facing AI risk management system for e-commerce return abuse detection. "
        "Demo environment — synthetic data only."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Create DB tables on startup if they don't exist."""
    create_tables()
    logger.info("ReturnShield AI backend started. Database tables ready.")


# FRONTEND DIRECTORY — now serves from React/Vite dist build
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")

# ============================================================
# HEALTH & ROOT
# ============================================================

@app.get("/api", tags=["Health"])
def root():
    return {
        "service": "ReturnShield AI",
        "version": "2.0.0",
        "status": "online",
        "note": "Demo environment — synthetic data",
        "docs": "/docs",
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        from ml.predict import get_predictor
        predictor = get_predictor()
        model_loaded = predictor.pipeline is not None
    except Exception:
        model_loaded = False

    try:
        db.execute(models.Customer.__table__.select().limit(1))
        db_status = "connected"
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        database=db_status,
        version="2.0.0",
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard/overview", response_model=DashboardOverview, tags=["Dashboard"])
def dashboard_overview(db: Session = Depends(get_db)):
    """
    Live KPI metrics for the merchant dashboard.
    Reads from investigations table (returns that have been scored).
    For unseeded state, falls back to return_features.csv summary.
    """
    try:
        # Try database first
        cases = db.query(models.Investigation).all()
        if cases:
            total = len(cases)
            high = sum(1 for c in cases if c.risk_level == "HIGH")
            medium = sum(1 for c in cases if c.risk_level == "MEDIUM")
            low = sum(1 for c in cases if c.risk_level == "LOW")
            abusive = sum(1 for c in cases if c.risk_level in ("HIGH", "MEDIUM"))
            pending = sum(1 for c in cases if c.action_taken == "PENDING")
            avg_score = sum(c.risk_score or 0 for c in cases) / total if total > 0 else 0.0
            abuse_rate = round((abusive / total) * 100, 2) if total > 0 else 0.0
        else:
            # Fallback: read from training CSV for initial dashboard
            import pandas as pd
            feat_path = os.path.join(PROJECT_ROOT, "artifacts", "return_features.csv")
            df = pd.read_csv(feat_path)
            total = len(df)
            abusive = int(df["potentially_abusive"].sum())
            normal = total - abusive
            abuse_rate = round((abusive / total) * 100, 2)
            # No SHAP in CSV — estimate from label distribution
            high = int(abusive * 0.55)
            medium = int(abusive * 0.45)
            low = normal
            avg_score = 0.0
            pending = 0
            cases = []

        total_returns_db = db.query(models.Return).count()

        return DashboardOverview(
            total_returns=total_returns_db if total_returns_db > 0 else total,
            abusive_flagged=high + medium if cases else abusive,
            normal_returns=low if cases else (total - abusive),
            abuse_rate_percent=abuse_rate,
            avg_risk_score=round(avg_score, 2),
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
            pending_reviews=pending,
        )
    except Exception as e:
        logger.error(f"dashboard_overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# CUSTOMERS
# ============================================================

@app.get("/api/customers", tags=["Customers"])
def list_customers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all customers (paginated)."""
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return [
        {
            "customer_id": c.customer_id,
            "city": c.city,
            "customer_segment": c.customer_segment,
            "signup_date": c.signup_date,
            "device_id": c.device_id,
            "address_id": c.address_id,
        }
        for c in customers
    ]


@app.get("/api/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get a single customer profile."""
    c = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return {
        "customer_id": c.customer_id,
        "city": c.city,
        "customer_segment": c.customer_segment,
        "signup_date": c.signup_date,
        "device_id": c.device_id,
        "address_id": c.address_id,
    }


@app.get("/api/customers/{customer_id}/orders", tags=["Customers"])
def get_customer_orders(customer_id: str, db: Session = Depends(get_db)):
    """Get all orders for a customer."""
    orders = db.query(models.Order).filter(models.Order.customer_id == customer_id).all()
    return [
        {
            "order_id": o.order_id,
            "order_date": o.order_date,
            "order_amount": o.order_amount,
            "payment_method": o.payment_method,
            "product_category": o.product_category,
            "order_status": o.order_status,
        }
        for o in orders
    ]


@app.get("/api/customers/{customer_id}/returns", tags=["Customers"])
def get_customer_returns(customer_id: str, db: Session = Depends(get_db)):
    """Get all returns for a customer."""
    returns = db.query(models.Return).filter(models.Return.customer_id == customer_id).all()
    return [
        {
            "return_id": r.return_id,
            "order_id": r.order_id,
            "return_date": r.return_date,
            "return_amount": r.return_amount,
            "return_reason": r.return_reason,
            "return_status": r.return_status,
        }
        for r in returns
    ]


@app.get("/api/customers/{customer_id}/refunds", tags=["Customers"])
def get_customer_refunds(customer_id: str, db: Session = Depends(get_db)):
    """Get all refunds for a customer."""
    refunds = db.query(models.Refund).filter(models.Refund.customer_id == customer_id).all()
    return [
        {
            "refund_id": r.refund_id,
            "return_id": r.return_id,
            "refund_date": r.refund_date,
            "refund_amount": r.refund_amount,
            "refund_status": r.refund_status,
        }
        for r in refunds
    ]


# ============================================================
# RETURNS
# ============================================================

@app.get("/api/returns", tags=["Returns"])
def list_returns(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all return requests (operational queue)."""
    returns = db.query(models.Return).offset(skip).limit(limit).all()
    return [
        {
            "return_id": r.return_id,
            "customer_id": r.customer_id,
            "order_id": r.order_id,
            "return_date": r.return_date,
            "return_amount": r.return_amount,
            "return_reason": r.return_reason,
            "return_status": r.return_status,
        }
        for r in returns
    ]


@app.get("/api/returns/{return_id}", tags=["Returns"])
def get_return(return_id: str, db: Session = Depends(get_db)):
    """Get details of a specific return request."""
    r = db.query(models.Return).filter(models.Return.return_id == return_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Return '{return_id}' not found.")
    return {
        "return_id": r.return_id,
        "customer_id": r.customer_id,
        "order_id": r.order_id,
        "return_date": r.return_date,
        "return_amount": r.return_amount,
        "return_reason": r.return_reason,
        "return_status": r.return_status,
    }


# ============================================================
# RISK SCORING
# ============================================================

@app.post("/api/risk/score", response_model=RiskScoreResponse, tags=["Risk"])
def score_risk(request: RiskScoreRequest, db: Session = Depends(get_db)):
    """
    Core endpoint: Takes customer_id + return_id,
    runs XGBoost + SHAP, returns risk score and recommendation.
    Also creates an Investigation case automatically.
    """
    try:
        result = risk_service.score_return_request(
            customer_id=request.customer_id,
            return_id=request.return_id,
        )
        # Auto-create investigation case
        investigation_service.create_investigation(db, result)
        return RiskScoreResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"risk/score error: {e}")
        raise HTTPException(status_code=500, detail=f"Risk scoring failed: {str(e)}")


# ============================================================
# MERCHANT ACTIONS
# ============================================================

@app.post("/api/returns/{return_id}/approve", response_model=ActionResponse, tags=["Actions"])
def approve_return(return_id: str, body: ActionRequest, db: Session = Depends(get_db)):
    """Merchant approves a return request."""
    return _take_action(db, return_id, "APPROVE", body)


@app.post("/api/returns/{return_id}/verify", response_model=ActionResponse, tags=["Actions"])
def verify_return(return_id: str, body: ActionRequest, db: Session = Depends(get_db)):
    """Merchant flags return for additional verification."""
    return _take_action(db, return_id, "VERIFY", body)


@app.post("/api/returns/{return_id}/manual-review", response_model=ActionResponse, tags=["Actions"])
def manual_review_return(return_id: str, body: ActionRequest, db: Session = Depends(get_db)):
    """Merchant sends return for manual review team."""
    return _take_action(db, return_id, "MANUAL_REVIEW", body)


def _take_action(db: Session, return_id: str, action: str, body: ActionRequest) -> ActionResponse:
    # Find investigation case for this return
    case = db.query(models.Investigation).filter(
        models.Investigation.return_id == return_id
    ).order_by(models.Investigation.created_at.desc()).first()

    # Update Return record status if it exists
    ret = db.query(models.Return).filter(models.Return.return_id == return_id).first()
    if ret:
        ret.return_status = action
        db.commit()

    if not case:
        if ret:
            try:
                risk_res = risk_service.score_return_request(
                    customer_id=ret.customer_id,
                    return_id=return_id,
                )
                case = investigation_service.create_investigation(db, risk_res)
            except Exception as e:
                logger.warning(f"Could not auto-score {return_id}: {e}")

        if not case:
            case = models.Investigation(
                case_id=f"CASE-{uuid.uuid4().hex[:10].upper()}",
                return_id=return_id,
                customer_id=ret.customer_id if ret else "UNKNOWN",
                order_id=ret.order_id if ret else "",
                risk_score=50.0,
                risk_level="MEDIUM",
                recommendation=action,
                action_taken="PENDING",
            )
            db.add(case)
            db.commit()
            db.refresh(case)

    updated = investigation_service.take_action(
        db, case.case_id, action, body.performed_by, body.notes
    )

    return ActionResponse(
        case_id=updated.case_id,
        return_id=updated.return_id,
        customer_id=updated.customer_id,
        risk_score=updated.risk_score,
        risk_level=updated.risk_level,
        action_taken=updated.action_taken,
        action_by=updated.action_by,
        action_notes=updated.action_notes,
        updated_at=str(updated.updated_at) if updated.updated_at else None,
    )


# ============================================================
# INVESTIGATIONS
# ============================================================

@app.get("/api/investigations", tags=["Investigations"])
def list_investigations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all investigation cases (newest first)."""
    cases = investigation_service.list_investigations(db, skip=skip, limit=limit)
    return [
        {
            "case_id": c.case_id,
            "return_id": c.return_id,
            "customer_id": c.customer_id,
            "risk_score": c.risk_score,
            "risk_level": c.risk_level,
            "action_taken": c.action_taken,
            "recommendation": c.recommendation,
            "created_at": str(c.created_at) if c.created_at else None,
        }
        for c in cases
    ]


@app.get("/api/investigations/{case_id}", tags=["Investigations"])
def get_investigation(case_id: str, db: Session = Depends(get_db)):
    """Get full investigation case details including SHAP factors."""
    try:
        case = investigation_service.get_investigation(db, case_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    factors = []
    try:
        factors = json.loads(case.top_risk_factors or "[]")
    except Exception:
        pass

    return {
        "case_id": case.case_id,
        "return_id": case.return_id,
        "customer_id": case.customer_id,
        "order_id": case.order_id,
        "risk_score": case.risk_score,
        "risk_level": case.risk_level,
        "recommendation": case.recommendation,
        "ai_summary": case.ai_summary,
        "top_risk_factors": factors,
        "action_taken": case.action_taken,
        "action_by": case.action_by,
        "action_notes": case.action_notes,
        "created_at": str(case.created_at) if case.created_at else None,
        "updated_at": str(case.updated_at) if case.updated_at else None,
    }


@app.post("/api/investigations/{case_id}/ai-summary", response_model=AISummaryResponse, tags=["Investigations"])
def regenerate_ai_summary(case_id: str, db: Session = Depends(get_db)):
    """Regenerate AI narrative summary for an investigation case."""
    try:
        summary = investigation_service.generate_ai_summary(db, case_id)
        return AISummaryResponse(case_id=case_id, ai_summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MODEL METRICS
# ============================================================

@app.get("/api/metrics", tags=["Model"])
def get_model_metrics():
    """Returns actual XGBoost evaluation metrics from artifacts/metrics.json."""
    try:
        metrics = risk_service.get_model_metrics()
        return metrics
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/thresholds", tags=["Model"])
def get_threshold_analysis():
    """Returns threshold sensitivity analysis (precision/recall tradeoff)."""
    return risk_service.get_threshold_analysis()


# ============================================================
# FRONTEND STATIC FILES MOUNT
# ============================================================

if os.path.exists(FRONTEND_DIR):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found"}

    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
