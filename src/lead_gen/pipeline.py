"""Orchestrates the four agents end-to-end: discover -> enrich -> score -> outreach."""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import models
from .agents.discovery import DiscoveryAgent
from .agents.enrichment import EnrichmentAgent
from .agents.outreach import OutreachAgent
from .agents.scoring import ScoringAgent


def _icp_to_dict(icp: models.ICP) -> dict:
    return {
        "id": icp.id,
        "name": icp.name,
        "industry": icp.industry,
        "company_size": icp.company_size,
        "geography": icp.geography,
        "pain_points": icp.pain_points,
        "keywords": icp.keywords or [],
    }


def run_for_icp(db: Session, icp_id: int, max_leads: int = 5) -> list[models.Lead]:
    """Run the full pipeline for an ICP and persist the resulting leads."""
    icp = db.get(models.ICP, icp_id)
    if icp is None:
        raise ValueError(f"ICP {icp_id} not found")
    buyer = db.get(models.Buyer, icp.buyer_id)
    icp_d = _icp_to_dict(icp)
    buyer_d = {"id": buyer.id, "name": buyer.name, "email": buyer.email} if buyer else {}

    discovery = DiscoveryAgent()
    enrichment = EnrichmentAgent()
    scoring = ScoringAgent()
    outreach = OutreachAgent()

    prospects = discovery.find_prospects(icp_d, max_results=max_leads)
    created: list[models.Lead] = []

    for prospect in prospects:
        enriched = enrichment.enrich(prospect)
        sc = scoring.score(enriched, icp_d)
        out = outreach.draft(enriched, icp_d, buyer_d)

        lead = models.Lead(
            icp_id=icp.id,
            company_name=enriched.get("company_name", "Unknown"),
            website=enriched.get("website"),
            industry=enriched.get("industry"),
            employee_count=enriched.get("employee_count"),
            location=enriched.get("location"),
            contact_name=enriched.get("contact_name"),
            contact_title=enriched.get("contact_title"),
            contact_email=enriched.get("contact_email"),
            enrichment={
                "tech_stack": enriched.get("tech_stack", []),
                "buying_signals": enriched.get("buying_signals", []),
                "description": enriched.get("description"),
            },
            score=float(sc.get("score", 0)),
            score_reasoning=sc.get("reasoning", ""),
            outreach_email=out.get("email"),
            outreach_followup=out.get("followup"),
            status="ready",
        )
        db.add(lead)
        created.append(lead)

    db.commit()
    for lead in created:
        db.refresh(lead)
    return created
