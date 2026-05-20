"""ORM models and Pydantic schemas for the lead-gen domain."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# -------- ORM --------

class Buyer(Base):
    """A company purchasing leads from us."""
    __tablename__ = "buyers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    icps: Mapped[list["ICP"]] = relationship(back_populates="buyer", cascade="all, delete-orphan")


class ICP(Base):
    """Ideal Customer Profile defined by a buyer."""
    __tablename__ = "icps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"))
    name: Mapped[str] = mapped_column(String(200))
    industry: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)  # "1-10", "11-50", etc.
    geography: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    pain_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    buyer: Mapped[Buyer] = relationship(back_populates="icps")


class Lead(Base):
    """An enriched, scored prospective client."""
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icp_id: Mapped[int] = mapped_column(ForeignKey("icps.id"))
    company_name: Mapped[str] = mapped_column(String(200))
    website: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    enrichment: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)  # tech stack, signals, etc.
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outreach_email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outreach_followup: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Delivery tracking
    message_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bounced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # new|enriched|scored|ready|sent|delivered|opened|replied|bounced|sold
    status: Mapped[str] = mapped_column(String(40), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Order(Base):
    """A buyer purchasing a lead."""
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("buyers.id"))
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"))
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    # Stripe / payments tracking
    payment_session_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    payment_provider: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(40), default="pending")  # pending|paid|failed|refunded
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# -------- Pydantic schemas --------

class ICPIn(BaseModel):
    buyer_id: int
    name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    geography: Optional[str] = None
    pain_points: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class ICPOut(ICPIn):
    id: int
    model_config = {"from_attributes": True}


class BuyerIn(BaseModel):
    name: str
    email: str


class BuyerOut(BuyerIn):
    id: int
    model_config = {"from_attributes": True}


class LeadOut(BaseModel):
    id: int
    icp_id: int
    company_name: str
    website: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    location: Optional[str]
    contact_name: Optional[str]
    contact_title: Optional[str]
    contact_email: Optional[str]
    score: Optional[float]
    score_reasoning: Optional[str]
    status: str
    model_config = {"from_attributes": True}


class LeadFull(LeadOut):
    enrichment: Optional[dict]
    outreach_email: Optional[str]
    outreach_followup: Optional[str]
    message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None


class SendOutreachRequest(BaseModel):
    use_followup: bool = False


class PipelineRequest(BaseModel):
    icp_id: int
    max_leads: int = 5


class OrderIn(BaseModel):
    buyer_id: int
    lead_id: int


class CheckoutRequest(BaseModel):
    buyer_id: int
    lead_id: int
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    order_id: int
    session_id: Optional[str]
    url: Optional[str]
    payment_status: str
    provider: str
