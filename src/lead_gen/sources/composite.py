"""Composite source: tries multiple sources in order and merges unique results."""
from __future__ import annotations

from typing import Any

from .base import DiscoverySource


class CompositeSource(DiscoverySource):
    name = "composite"

    def __init__(self, sources: list[DiscoverySource]) -> None:
        self.sources = sources

    def search(self, icp: dict[str, Any], max_results: int) -> list[dict[str, Any]]:
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []
        for src in self.sources:
            for p in src.search(icp, max_results):
                key = (p.get("website") or p.get("company_name") or "").lower()
                if key and key not in seen:
                    seen.add(key)
                    merged.append(p)
                if len(merged) >= max_results:
                    return merged
        return merged
