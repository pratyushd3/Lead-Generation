"""Marketplace logic: pricing leads and recording purchases."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import models
from .payments import payments


def price_for(lead: models.Lead) -> int:
    """Return price in cents based on score. Higher score = higher price."""
    if lead.score is None:
        return 1000  # $10 default
    if lead.score >= 85:
        return 5000  # $50
    if lead.score >= 70:
        return 3000  # $30
    if lead.score >= 50:
        return 1500  # $15
    return 500  # $5


def _validate(db: Session, buyer_id: int, lead_id: int) -> tuple[models.Buyer, models.Lead]:
    buyer = db.get(models.Buyer, buyer_id)
    lead = db.get(models.Lead, lead_id)
    if buyer is None or lead is None:
        raise ValueError("buyer or lead not found")
    if lead.status == "sold":
        raise ValueError("lead already sold")
    return buyer, lead


def purchase(db: Session, buyer_id: int, lead_id: int) -> models.Order:
    """Direct/admin purchase: creates an order and immediately marks it paid + sold."""
    _, lead = _validate(db, buyer_id, lead_id)
    order = models.Order(
        buyer_id=buyer_id,
        lead_id=lead_id,
        price_cents=price_for(lead),
        payment_provider="manual",
        payment_status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    lead.status = "sold"
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def start_checkout(
    db: Session,
    buyer_id: int,
    lead_id: int,
    success_url: str | None = None,
    cancel_url: str | None = None,
) -> tuple[models.Order, dict]:
    """Create a pending order and a payment-provider checkout session.

    In mock mode the order is auto-completed (status=paid, lead=sold).
    In Stripe mode the order remains pending until the webhook fires.
    """
    _, lead = _validate(db, buyer_id, lead_id)
    order = models.Order(
        buyer_id=buyer_id,
        lead_id=lead_id,
        price_cents=price_for(lead),
        payment_status="pending",
    )
    db.add(order)
    db.flush()  # get order.id

    session = payments.create_checkout(
        order_id=order.id,
        lead_company=lead.company_name,
        amount_cents=order.price_cents,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    order.payment_provider = session.get("provider")
    order.payment_session_id = session.get("session_id")

    if session.get("status") == "paid":
        # Mock provider: complete immediately.
        order.payment_status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        lead.status = "sold"

    db.commit()
    db.refresh(order)
    return order, session


def fulfill_by_session_id(db: Session, session_id: str) -> models.Order | None:
    """Mark an order as paid based on Stripe webhook completion."""
    order = (
        db.query(models.Order)
        .filter(models.Order.payment_session_id == session_id)
        .first()
    )
    if order is None or order.payment_status == "paid":
        return order

    order.payment_status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    lead = db.get(models.Lead, order.lead_id)
    if lead is not None:
        lead.status = "sold"
    db.commit()
    db.refresh(order)
    return order
