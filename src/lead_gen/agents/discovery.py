"""Discovery agent: ICP -> candidate prospect companies.

The agent delegates to a configurable DiscoverySource (mock | google_cse |
hunter | composite). Real sources fall back to the mock pool if their API
keys are missing or a call fails, so the pipeline never hard-fails.
"""
from __future__ import annotations

from typing import Any

from ..config import settings
from ..sources import get_source
from .base import Agent


class DiscoveryAgent(Agent):
    name = "discovery"

    def __init__(self, source_name: str | None = None) -> None:
        self.source = get_source(source_name or settings.discovery_source)

    def find_prospects(self, icp: dict[str, Any], max_results: int = 10) -> list[dict[str, Any]]:
        self.log(f"using source={self.source.name!r} for ICP={icp.get('name')!r}")
        return self.source.search(icp, max_results=max_results)
