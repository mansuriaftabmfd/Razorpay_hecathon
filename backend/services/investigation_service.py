# ============================================================
# backend/services/investigation_service.py — Case Management
# ============================================================
# Manages the full lifecycle of return fraud investigation cases:
# creation, status updates, Groq LLM narrative explanations, and
# immutable audit logging.
# ============================================================

import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Investigation, AuditLog

# Groq AI client initialization (optional, falls back gracefully if unconfigured)
_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            _groq_client = Groq(api_key=api_key)
    except ImportError:
        pass
    return _groq_client


def _call_groq(prompt: str) -> str:
    """Executes Groq LLaMA-3 inference for analyst-level narrative summaries."""
    client = _get_groq_client()
    if client is None:
        return ""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior fraud analyst at a fintech risk platform. "
                        "Write a concise, professional investigation summary (3-4 sentences). "
                        "Be direct, factual, and actionable for e-commerce merchants."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def create_investigation(db: Session, risk_result: dict) -> Investigation:
    """
    Creates and persists a new investigation case following ML risk scoring.

    Args:
        db: SQLAlchemy session
        risk_result: Evaluation dictionary from risk_service.score_return_request()

    Returns:
        Persisted Investigation ORM instance
    """
    case_id = risk_result.get("case_id", f"CASE-{uuid.uuid4().hex[:10].upper()}")

    # Serialize SHAP factors into JSON string for persistence
    factors_json = json.dumps(risk_result.get("top_risk_factors", []))

    # Generate analytical narrative explanation
    ai_summary = _generate_ai_summary(risk_result)

    case = Investigation(
        case_id=case_id,
        return_id=risk_result["return_id"],
        customer_id=risk_result["customer_id"],
        order_id=risk_result.get("order_id", ""),
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        recommendation=risk_result["action"],
        ai_summary=ai_summary,
        top_risk_factors=factors_json,
        action_taken="PENDING",
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Record initial risk scoring event to immutable audit log
    _write_audit(
        db,
        case_id,
        risk_result["return_id"],
        risk_result["customer_id"],
        "RISK_SCORED",
        "system",
        f"Risk score: {risk_result['risk_score']}%, Level: {risk_result['risk_level']}",
    )

    return case


def get_investigation(db: Session, case_id: str) -> Investigation:
    """Retrieves an existing investigation case by its unique case_id."""
    case = db.query(Investigation).filter(Investigation.case_id == case_id).first()
    if not case:
        raise ValueError(f"Investigation case '{case_id}' not found.")
    return case


def list_investigations(db: Session, skip: int = 0, limit: int = 50) -> list:
    """Returns chronologically ordered investigation cases (newest first)."""
    return (
        db.query(Investigation)
        .order_by(Investigation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def take_action(
    db: Session,
    case_id: str,
    action: str,
    performed_by: str = "merchant",
    notes: str = "",
) -> Investigation:
    """
    Applies and audits merchant decision: APPROVE / VERIFY / MANUAL_REVIEW.

    Args:
        db: SQLAlchemy session
        case_id: Target investigation case ID
        action: Decision action (APPROVE, VERIFY, MANUAL_REVIEW)
        performed_by: Operator or user ID
        notes: Operator investigation notes
    """
    valid_actions = {"APPROVE", "VERIFY", "MANUAL_REVIEW"}
    if action not in valid_actions:
        raise ValueError(f"Invalid action '{action}'. Must be one of: {valid_actions}")

    case = get_investigation(db, case_id)
    case.action_taken = action
    case.action_by = performed_by
    case.action_notes = notes
    case.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(case)

    # Append immutable compliance audit log
    _write_audit(db, case_id, case.return_id, case.customer_id, action, performed_by, notes)

    return case


def generate_ai_summary(db: Session, case_id: str) -> str:
    """
    Generates Groq LLM-powered narrative summary, falling back to structured templates.
    """
    case = get_investigation(db, case_id)
    factors = json.loads(case.top_risk_factors or "[]")
    risk_result = {
        "return_id": case.return_id,
        "customer_id": case.customer_id,
        "risk_score": case.risk_score,
        "risk_level": case.risk_level,
        "action": case.recommendation,
        "top_risk_factors": factors,
    }

    # Attempt LLM generation first
    groq_prompt = _build_groq_prompt(risk_result)
    summary = _call_groq(groq_prompt)

    # Fallback to structured domain template if unavailable
    if not summary:
        summary = _generate_ai_summary(risk_result)

    case.ai_summary = summary
    db.commit()
    return summary


def _build_groq_prompt(risk_result: dict) -> str:
    """Constructs prompt for Groq LLaMA-3 analytical explanation."""
    factors = risk_result.get("top_risk_factors", [])
    top_factors = ", ".join(
        f"{f.get('feature','?')} ({'+' if f.get('direction') == 'increases_risk' else '-'}{abs(f.get('shap_impact', 0)):.3f})"
        for f in factors[:3]
    ) or "none identified"

    return (
        f"Write an investigation summary for this return fraud case:\n"
        f"- Customer: {risk_result.get('customer_id')}\n"
        f"- Return: {risk_result.get('return_id')}\n"
        f"- Risk Score: {risk_result.get('risk_score', 0):.1f}% ({risk_result.get('risk_level')} risk)\n"
        f"- Recommended Action: {risk_result.get('action')}\n"
        f"- Top SHAP Risk Drivers: {top_factors}\n"
        f"Write 3-4 professional sentences summarising what this score means and what the merchant should do."
    )


def _generate_ai_summary(risk_result: dict) -> str:
    """
    Deterministic domain narrative generator based on calibrated risk score and SHAP weights.
    """
    risk_level = risk_result.get("risk_level", "UNKNOWN")
    risk_score = risk_result.get("risk_score", 0)
    action = risk_result.get("action", "PENDING")
    return_id = risk_result.get("return_id", "")
    customer_id = risk_result.get("customer_id", "")
    factors = risk_result.get("top_risk_factors", [])

    top_factors_text = ""
    for i, f in enumerate(factors[:3], 1):
        feat = f.get("feature", "").replace("_", " ").title()
        shap = f.get("shap_impact", 0)
        direction = "increases" if f.get("direction") == "increases_risk" else "reduces"
        top_factors_text += f"  {i}. {feat} (SHAP impact: {shap:.3f}) — {direction} risk\n"

    if risk_level == "HIGH":
        tone = (
            f"Return request {return_id} from customer {customer_id} has been flagged as HIGH RISK "
            f"with a score of {risk_score:.1f}%. "
            f"Customer profile indicates multiple anomalous return indicators. "
            f"Recommended Action: {action} — Verify physical item upon courier receipt."
        )
    elif risk_level == "MEDIUM":
        tone = (
            f"Return request {return_id} from customer {customer_id} is evaluated as MEDIUM RISK "
            f"with a score of {risk_score:.1f}%. "
            f"Recommended Action: {action} — Require customer OTP verification before refund processing."
        )
    else:
        tone = (
            f"Return request {return_id} from customer {customer_id} is evaluated as LOW RISK "
            f"with a score of {risk_score:.1f}%. "
            f"No abusive return signals detected. "
            f"Recommended Action: {action} — Instant refund recommended."
        )

    return tone


def _write_audit(
    db: Session,
    case_id: str,
    return_id: str,
    customer_id: str,
    action: str,
    performed_by: str,
    details: str,
):
    """Appends an immutable entry to the compliance audit log."""
    log = AuditLog(
        case_id=case_id,
        return_id=return_id,
        customer_id=customer_id,
        action=action,
        performed_by=performed_by,
        details=details,
    )
    db.add(log)
    db.commit()
