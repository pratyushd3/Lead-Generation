"""Mock source: filters the seeded prospect pool by ICP traits."""
from __future__ import annotations

from typing import Any

from .. import seed
from .base import DiscoverySource


class MockSource(DiscoverySource):
    name = "mock"

    def search(self, icp: dict[str, Any], max_results: int) -> list[dict[str, Any]]:
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

        return [p for p in seed.PROSPECT_POOL if matches(p)][:max_results]
