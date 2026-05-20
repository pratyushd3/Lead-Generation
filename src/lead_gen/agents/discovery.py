"""Discovery agent: ICP -> candidate prospect companies.

In production this would call sources like Apollo, LinkedIn Sales Nav, Crunchbase,
Google Maps, or web search. For the MVP we filter a seeded mock pool by ICP traits.
"""
from __future__ import annotations

from typing import Any

from .. import seed
from .base import Agent


class DiscoveryAgent(Agent):
    name = "discovery"

    def find_prospects(self, icp: dict[str, Any], max_results: int = 10) -> list[dict[str, Any]]:
        self.log(f"searching for prospects matching ICP={icp.get('name')!r}")
        pool = seed.PROSPECT_POOL
        kw = {k.lower() for k in (icp.get("keywords") or [])}
        industry = (icp.get("industry") or "").lower()

        def matches(p: dict[str, Any]) -> bool:
            blob = " ".join(
                str(p.get(f, "")) for f in ("industry", "description", "tags")
            ).lower()
            if industry and industry not in blob:
                return False
            if kw and not any(k in blob for k in kw):
                return False
            return True

        results = [p for p in pool if matches(p)]
        return results[:max_results]
