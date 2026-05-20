"""End-to-end CLI demo: seed -> run pipeline -> print results.

Usage:
    python scripts/run_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lead_gen import models, seed  # noqa: E402
from lead_gen.db import SessionLocal, init_db  # noqa: E402
from lead_gen.pipeline import run_for_icp  # noqa: E402


def ensure_seed(db) -> int:
    if db.query(models.Buyer).count() == 0:
        buyer = models.Buyer(**seed.SAMPLE_BUYERS[0])
        db.add(buyer)
        db.flush()
        for icp_data in seed.SAMPLE_ICPS:
            db.add(models.ICP(buyer_id=buyer.id, **icp_data))
        db.commit()
    icp = db.query(models.ICP).first()
    return icp.id


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        icp_id = ensure_seed(db)
        leads = run_for_icp(db, icp_id, max_leads=5)
        print(f"\nGenerated {len(leads)} leads for ICP #{icp_id}\n" + "=" * 60)
        for lead in sorted(leads, key=lambda l: (l.score or 0), reverse=True):
            print(
                f"\n[{lead.score:5.1f}] {lead.company_name} "
                f"({lead.industry}, {lead.employee_count} ppl, {lead.location})"
            )
            print(f"  contact: {lead.contact_name} <{lead.contact_email}> - {lead.contact_title}")
            print(f"  why:     {lead.score_reasoning}")
            print(f"  email:   {(lead.outreach_email or '').splitlines()[0]} ...")
    finally:
        db.close()


if __name__ == "__main__":
    main()
