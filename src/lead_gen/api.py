"""FastAPI app exposing the lead-gen agency as an HTTP service."""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import marketplace, models, pipeline, seed
from .config import settings
from .db import SessionLocal, get_session, init_db
from .mailer import mailer, parse_email


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    _ensure_seed()
    yield


def _ensure_seed() -> None:
    """Seed sample buyers + ICPs if the DB is empty (idempotent)."""
    db = SessionLocal()
    try:
        if db.query(models.Buyer).count() > 0:
            return
        buyer = models.Buyer(**seed.SAMPLE_BUYERS[0])
        db.add(buyer)
        db.flush()
        for icp_data in seed.SAMPLE_ICPS:
            db.add(models.ICP(buyer_id=buyer.id, **icp_data))
        db.commit()
    finally:
        db.close()


app = FastAPI(
    title="Lead Generation Agency",
    description="AI agents that discover, enrich, score, and draft outreach to prospective clients.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "name": "Lead Generation Agency",
        "endpoints": [
            "POST /buyers",
            "GET  /buyers",
            "POST /icps",
            "GET  /icps",
            "POST /pipeline/run",
            "GET  /leads?icp_id=&min_score=",
            "GET  /leads/{id}",
            "POST /leads/{id}/send",
            "POST /marketplace/purchase",
            "POST /marketplace/checkout",
            "GET  /marketplace/orders",
            "POST /webhooks/resend",
            "POST /webhooks/stripe",
        ],
    }


# ---------- Buyers ----------

@app.post("/buyers", response_model=models.BuyerOut)
def create_buyer(payload: models.BuyerIn, db: Session = Depends(get_session)):
    buyer = models.Buyer(**payload.model_dump())
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


@app.get("/buyers", response_model=list[models.BuyerOut])
def list_buyers(db: Session = Depends(get_session)):
    return db.query(models.Buyer).all()


# ---------- ICPs ----------

@app.post("/icps", response_model=models.ICPOut)
def create_icp(payload: models.ICPIn, db: Session = Depends(get_session)):
    if db.get(models.Buyer, payload.buyer_id) is None:
        raise HTTPException(404, "buyer not found")
    icp = models.ICP(**payload.model_dump())
    db.add(icp)
    db.commit()
    db.refresh(icp)
    return icp


@app.get("/icps", response_model=list[models.ICPOut])
def list_icps(db: Session = Depends(get_session)):
    return db.query(models.ICP).all()


# ---------- Pipeline ----------

@app.post("/pipeline/run", response_model=list[models.LeadOut])
def run_pipeline(payload: models.PipelineRequest, db: Session = Depends(get_session)):
    try:
        return pipeline.run_for_icp(db, payload.icp_id, payload.max_leads)
    except ValueError as e:
        raise HTTPException(404, str(e))


# ---------- Leads ----------

@app.get("/leads", response_model=list[models.LeadOut])
def list_leads(
    icp_id: int | None = None,
    min_score: float = 0.0,
    db: Session = Depends(get_session),
):
    q = db.query(models.Lead)
    if icp_id is not None:
        q = q.filter(models.Lead.icp_id == icp_id)
    if min_score > 0:
        q = q.filter(models.Lead.score >= min_score)
    return q.order_by(models.Lead.score.desc().nullslast()).all()


@app.get("/leads/{lead_id}", response_model=models.LeadFull)
def get_lead(lead_id: int, db: Session = Depends(get_session)):
    lead = db.get(models.Lead, lead_id)
    if lead is None:
        raise HTTPException(404, "lead not found")
    return lead


@app.post("/leads/{lead_id}/send", response_model=models.LeadFull)
def send_outreach(
    lead_id: int,
    payload: models.SendOutreachRequest,
    db: Session = Depends(get_session),
):
    """Send the outreach email (or follow-up) via the configured mailer."""
    lead = db.get(models.Lead, lead_id)
    if lead is None:
        raise HTTPException(404, "lead not found")
    if not lead.contact_email:
        raise HTTPException(400, "lead has no contact_email")

    raw = lead.outreach_followup if payload.use_followup else lead.outreach_email
    if not raw:
        raise HTTPException(400, "no outreach draft available; run the pipeline first")

    subject, body = parse_email(raw)
    result = mailer.send(
        to_email=lead.contact_email,
        to_name=lead.contact_name,
        subject=subject,
        body=body,
    )
    if result.get("status") == "error":
        raise HTTPException(502, f"mailer error: {result.get('error')}")

    lead.message_id = result.get("message_id")
    lead.sent_at = datetime.now(timezone.utc)
    lead.status = "sent"
    db.commit()
    db.refresh(lead)
    return lead


# ---------- Webhooks ----------

@app.post("/webhooks/resend")
async def resend_webhook(request: Request, db: Session = Depends(get_session)):
    """Update lead delivery status from Resend events.

    Handles event types: email.delivered, email.opened, email.bounced,
    email.complained. Replies require inbound parsing and are not delivered
    by Resend directly; expose a separate /webhooks/inbound for that.
    """
    payload = await request.json()
    event = payload.get("type") or payload.get("event") or ""
    data = payload.get("data") or {}
    message_id = data.get("email_id") or data.get("id") or data.get("message_id")
    if not message_id:
        return {"ok": True, "matched": False}

    lead = db.query(models.Lead).filter(models.Lead.message_id == message_id).first()
    if lead is None:
        return {"ok": True, "matched": False}

    now = datetime.now(timezone.utc)
    if event.endswith("delivered"):
        lead.delivered_at = now
        lead.status = "delivered"
    elif event.endswith("opened"):
        lead.opened_at = lead.opened_at or now
        if lead.status in {"sent", "delivered"}:
            lead.status = "opened"
    elif event.endswith("bounced") or event.endswith("complained"):
        lead.bounced_at = now
        lead.status = "bounced"

    db.commit()
    return {"ok": True, "matched": True, "lead_id": lead.id, "status": lead.status}


@app.post("/webhooks/inbound")
async def inbound_webhook(request: Request, db: Session = Depends(get_session)):
    """Generic inbound-email webhook to mark a lead as replied.

    Accepts JSON with one of: in_reply_to (message id we sent), or from + subject.
    """
    payload = await request.json()
    in_reply_to = payload.get("in_reply_to") or payload.get("message_id")
    from_email = (payload.get("from") or "").lower()

    lead = None
    if in_reply_to:
        lead = db.query(models.Lead).filter(models.Lead.message_id == in_reply_to).first()
    if lead is None and from_email:
        lead = db.query(models.Lead).filter(models.Lead.contact_email == from_email).first()
    if lead is None:
        return {"ok": True, "matched": False}

    lead.replied_at = datetime.now(timezone.utc)
    lead.status = "replied"
    db.commit()
    return {"ok": True, "matched": True, "lead_id": lead.id}


# ---------- Marketplace ----------

@app.post("/marketplace/purchase")
def purchase_lead(payload: models.OrderIn, db: Session = Depends(get_session)):
    """Direct/admin purchase: skips checkout, marks order paid + lead sold."""
    try:
        order = marketplace.purchase(db, payload.buyer_id, payload.lead_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "order_id": order.id,
        "buyer_id": order.buyer_id,
        "lead_id": order.lead_id,
        "price_cents": order.price_cents,
        "payment_status": order.payment_status,
        "created_at": order.created_at,
    }


@app.post("/marketplace/checkout", response_model=models.CheckoutResponse)
def create_checkout(payload: models.CheckoutRequest, db: Session = Depends(get_session)):
    """Create a payment-provider checkout session for a lead."""
    try:
        order, session = marketplace.start_checkout(
            db, payload.buyer_id, payload.lead_id, payload.success_url, payload.cancel_url
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    if session.get("status") == "error":
        raise HTTPException(502, f"payments error: {session.get('error')}")
    return models.CheckoutResponse(
        order_id=order.id,
        session_id=session.get("session_id"),
        url=session.get("url"),
        payment_status=order.payment_status,
        provider=session.get("provider", "mock"),
    )


@app.get("/marketplace/orders")
def list_orders(db: Session = Depends(get_session)):
    rows = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "buyer_id": o.buyer_id,
            "lead_id": o.lead_id,
            "price_cents": o.price_cents,
            "payment_status": o.payment_status,
            "payment_provider": o.payment_provider,
            "paid_at": o.paid_at,
            "created_at": o.created_at,
        }
        for o in rows
    ]


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_session)):
    """Handle Stripe checkout.session.completed events.

    Verifies signature with STRIPE_WEBHOOK_SECRET if configured; otherwise
    accepts the raw payload (useful for local mock testing).
    """
    from .payments import payments as pay

    body = await request.body()
    sig = request.headers.get("stripe-signature")
    event = pay.verify_webhook(body, sig)
    if event is None:
        # Fallback: parse JSON directly (useful when running without Stripe).
        try:
            event = await request.json()
        except Exception:
            raise HTTPException(400, "invalid webhook payload")

    if event.get("type") != "checkout.session.completed":
        return {"ok": True, "ignored": event.get("type")}

    session = (event.get("data") or {}).get("object") or {}
    session_id = session.get("id")
    if not session_id:
        return {"ok": True, "matched": False}

    order = marketplace.fulfill_by_session_id(db, session_id)
    if order is None:
        return {"ok": True, "matched": False}
    return {"ok": True, "order_id": order.id, "payment_status": order.payment_status}
