"""Scoring agent: enriched lead + ICP -> fit score (0-100) with reasoning."""
from __future__ import annotations

from typing import Any

from ..llm import llm
from .base import Agent


class ScoringAgent(Agent):
    name = "scoring"

    def score(self, lead: dict[str, Any], icp: dict[str, Any]) -> dict[str, Any]:
        self.log(f"scoring {lead.get('company_name')} vs ICP {icp.get('name')!r}")
        # Heuristic fallback: keyword overlap + industry match.
        kw = {k.lower() for k in (icp.get("keywords") or [])}
        blob = " ".join(
            str(lead.get(f, "")) for f in ("industry", "description", "tags", "tech_stack")
        ).lower()
        overlap = sum(1 for k in kw if k in blob)
        base = 40 + min(overlap * 12, 50)
        if (icp.get("industry") or "").lower() in blob:
            base = min(base + 10, 100)
        fallback = {
            "score": float(base),
            "reasoning": (
                f"Heuristic: {overlap} keyword matches; "
                f"industry {'matched' if (icp.get('industry') or '').lower() in blob else 'partial'}."
            ),
        }
        return llm.complete_json(
            system=(
                "You are a B2B lead-scoring agent. Given an Ideal Customer Profile (ICP) "
                "and a lead, return JSON {\"score\": 0-100 float, \"reasoning\": str}. "
                "Score based on industry, size, geography, keyword/pain-point alignment, "
                "and buying signals."
            ),
            user=f"ICP: {icp}\n\nLEAD: {lead}",
            fallback=fallback,
        )
