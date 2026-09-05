# backend/schemas.py
# ============================================================
# PYDANTIC SCHEMAS — Request & Response Validation
# ============================================================
# Yeh file define karti hai ki API ke request body aur
# response body mein kya data aayega.
# ============================================================

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Risk Scoring ─────────────────────────────────────────────

class RiskScoreRequest(BaseModel):
    """POST /api/risk/score ke liye input."""
    customer_id: str = Field(..., description="Customer ID, e.g. CUST00001")
    return_id: str = Field(..., description="Return ID, e.g. RET000001")


class ShapFactor(BaseModel):
    feature: str
    value: float
    shap_impact: float
    direction: str  # "increases_risk" or "decreases_risk"


class RiskScoreResponse(BaseModel):
    case_id: str
    return_id: str
    customer_id: str
    order_id: str
    risk_score: float
    risk_level: str           # LOW / MEDIUM / HIGH
    action: str               # APPROVE / VERIFY / MANUAL_REVIEW
    recommendation: str
    top_risk_factors: List[Dict[str, Any]]
    feature_snapshot: Dict[str, Any]
    prediction: int
    prediction_label: str
    scored_at: str


# ── Merchant Action ──────────────────────────────────────────

class ActionRequest(BaseModel):
    """POST /api/returns/{return_id}/approve|verify|manual-review"""
    performed_by: str = Field(default="merchant", description="Merchant user identifier")
    notes: str = Field(default="", description="Optional notes from the merchant")


class ActionResponse(BaseModel):
    case_id: str
    return_id: str
    customer_id: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    action_taken: Optional[str]
    action_by: Optional[str]
    action_notes: Optional[str]
    updated_at: Optional[str]


# ── Investigations ───────────────────────────────────────────

class InvestigationOut(BaseModel):
    case_id: str
    return_id: str
    customer_id: str
    order_id: Optional[str]
    risk_score: Optional[float]
    risk_level: Optional[str]
    recommendation: Optional[str]
    ai_summary: Optional[str]
    action_taken: Optional[str]
    action_by: Optional[str]
    action_notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class AISummaryResponse(BaseModel):
    case_id: str
    ai_summary: str


# ── Customers ────────────────────────────────────────────────

class CustomerOut(BaseModel):
    customer_id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    customer_segment: Optional[str]
    signup_date: Optional[str]
    device_id: Optional[str]
    address_id: Optional[str]

    class Config:
        from_attributes = True


# ── Returns ──────────────────────────────────────────────────

class ReturnOut(BaseModel):
    return_id: str
    customer_id: str
    order_id: str
    return_date: Optional[str]
    return_amount: Optional[float]
    return_reason: Optional[str]
    return_status: Optional[str]

    class Config:
        from_attributes = True


# ── Orders ───────────────────────────────────────────────────

class OrderOut(BaseModel):
    order_id: str
    customer_id: str
    order_date: Optional[str]
    order_amount: Optional[float]
    payment_method: Optional[str]
    product_category: Optional[str]
    order_status: Optional[str]

    class Config:
        from_attributes = True


# ── Dashboard ────────────────────────────────────────────────

class DashboardOverview(BaseModel):
    total_returns: int
    abusive_flagged: int
    normal_returns: int
    abuse_rate_percent: float
    avg_risk_score: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    pending_reviews: int


# ── Metrics ──────────────────────────────────────────────────

class ModelMetricsResponse(BaseModel):
    model: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    confusion_matrix: Dict[str, int]
    fp_fn_analysis: Dict[str, Any]


# ── Health ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database: str
    version: str
