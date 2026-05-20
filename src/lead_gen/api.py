"""FastAPI app exposing the lead-gen agency as an HTTP service."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import marketplace, models, pipeline, seed
from .db import SessionLocal, get_session, init_db


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
            "POST /marketplace/purchase",
            "GET  /marketplace/orders",
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


# ---------- Marketplace ----------

@app.post("/marketplace/purchase")
def purchase_lead(payload: models.OrderIn, db: Session = Depends(get_session)):
    try:
        order = marketplace.purchase(db, payload.buyer_id, payload.lead_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "order_id": order.id,
        "buyer_id": order.buyer_id,
        "lead_id": order.lead_id,
        "price_cents": order.price_cents,
        "created_at": order.created_at,
    }


@app.get("/marketplace/orders")
def list_orders(db: Session = Depends(get_session)):
    rows = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "buyer_id": o.buyer_id,
            "lead_id": o.lead_id,
            "price_cents": o.price_cents,
            "created_at": o.created_at,
        }
        for o in rows
    ]
