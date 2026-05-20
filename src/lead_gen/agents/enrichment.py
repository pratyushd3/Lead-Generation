"""Enrichment agent: prospect -> enriched lead with contact + signals."""
from __future__ import annotations

from typing import Any

from ..llm import llm
from .base import Agent


class EnrichmentAgent(Agent):
    name = "enrichment"

    def enrich(self, prospect: dict[str, Any]) -> dict[str, Any]:
        self.log(f"enriching {prospect.get('company_name')}")
        # Mock enrichment: synthesize plausible contact + signals.
        # Real impl would call Hunter, Apollo, Clearbit, web scraping, etc.
        domain = (prospect.get("website") or "").replace("https://", "").replace("http://", "").strip("/")
        first = "alex"
        contact_email = f"{first}@{domain}" if domain else None

        fallback = {
            "contact_name": "Alex Rivera",
            "contact_title": "Head of Operations",
            "contact_email": contact_email,
            "tech_stack": prospect.get("tags", [])[:3],
            "buying_signals": ["recent funding round", "hiring for ops roles"],
        }
        result = llm.complete_json(
            system=(
                "You are a B2B data enrichment agent. Given a company profile, "
                "produce a JSON object with keys: contact_name, contact_title, "
                "contact_email, tech_stack (list), buying_signals (list). "
                "Be realistic; if unsure, infer plausibly from the profile."
            ),
            user=str(prospect),
            fallback=fallback,
        )
        return {**prospect, **result}
