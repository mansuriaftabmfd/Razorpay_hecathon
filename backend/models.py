# backend/models.py
# ============================================================
# SQLAlchemy ORM Models — Database Tables
# ============================================================
# Yeh file define karti hai ki database mein kaun si tables
# hongi aur unke columns kaun se honge.
#
# Tables:
#   - customers         (raw CSV data mirrored)
#   - orders            (raw CSV data mirrored)
#   - returns           (raw CSV data mirrored)
#   - refunds           (raw CSV data mirrored)
#   - devices           (raw CSV data mirrored)
#   - addresses         (raw CSV data mirrored)
#   - investigations    (NEW: case management)
#   - audit_logs        (NEW: merchant action audit trail)
# ============================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)
    customer_segment = Column(String, nullable=True)
    signup_date = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    address_id = Column(String, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    order_date = Column(String, nullable=True)
    order_amount = Column(Float, nullable=True)
    payment_method = Column(String, nullable=True)
    product_category = Column(String, nullable=True)
    order_status = Column(String, nullable=True)


class Return(Base):
    __tablename__ = "returns"

    return_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    return_date = Column(String, nullable=True)
    return_amount = Column(Float, nullable=True)
    return_reason = Column(String, nullable=True)
    return_status = Column(String, nullable=True)


class Refund(Base):
    __tablename__ = "refunds"

    refund_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    return_id = Column(String, nullable=True)
    refund_date = Column(String, nullable=True)
    refund_amount = Column(Float, nullable=True)
    refund_status = Column(String, nullable=True)


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    device_type = Column(String, nullable=True)
    linked_accounts = Column(Integer, default=1)


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(String, primary_key=True, index=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    linked_accounts = Column(Integer, default=1)


class Investigation(Base):
    """
    Risk investigation case — created when a return request is risk-scored.
    Merchant can APPROVE, VERIFY, or send to MANUAL_REVIEW.
    """
    __tablename__ = "investigations"

    case_id = Column(String, primary_key=True, index=True)
    return_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    order_id = Column(String, nullable=True)

    # ML output
    risk_score = Column(Float, nullable=True)          # 0.0 to 100.0
    risk_level = Column(String, nullable=True)          # LOW / MEDIUM / HIGH
    recommendation = Column(String, nullable=True)      # APPROVE / VERIFY / MANUAL_REVIEW
    ai_summary = Column(Text, nullable=True)            # Generated AI narrative
    top_risk_factors = Column(Text, nullable=True)      # JSON string of SHAP factors

    # Merchant decision
    action_taken = Column(String, nullable=True)        # APPROVE / VERIFY / MANUAL_REVIEW / PENDING
    action_by = Column(String, nullable=True)           # Merchant user ID
    action_notes = Column(Text, nullable=True)          # Optional notes from merchant

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)


class AuditLog(Base):
    """
    Immutable audit trail of every merchant action.
    Spec: Every APPROVE / VERIFY / MANUAL_REVIEW must be logged.
    """
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, index=True, nullable=True)
    return_id = Column(String, index=True, nullable=True)
    customer_id = Column(String, nullable=True)

    action = Column(String, nullable=False)             # APPROVE / VERIFY / MANUAL_REVIEW / RISK_SCORED
    performed_by = Column(String, nullable=True)        # Merchant user / system
    details = Column(Text, nullable=True)               # JSON payload
    timestamp = Column(DateTime, server_default=func.now())
