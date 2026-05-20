"""Marketplace logic: pricing leads and recording purchases."""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import models


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


def purchase(db: Session, buyer_id: int, lead_id: int) -> models.Order:
    lead = db.get(models.Lead, lead_id)
    buyer = db.get(models.Buyer, buyer_id)
    if lead is None or buyer is None:
        raise ValueError("buyer or lead not found")
    if lead.status == "sold":
        raise ValueError("lead already sold")

    order = models.Order(buyer_id=buyer_id, lead_id=lead_id, price_cents=price_for(lead))
    lead.status = "sold"
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
