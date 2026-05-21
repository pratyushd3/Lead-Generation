"""Google Custom Search Engine discovery source.

Builds a query from the ICP and returns websites as candidate companies.
Requires GOOGLE_CSE_API_KEY and GOOGLE_CSE_ENGINE_ID. Falls back to the
mock source when keys are missing or the API call fails.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from ..config import settings
from .base import DiscoverySource
from .mock_source import MockSource


class GoogleCSESource(DiscoverySource):
    name = "google_cse"
    endpoint = "https://www.googleapis.com/customsearch/v1"

    def _query_for(self, icp: dict[str, Any]) -> str:
        parts: list[str] = []
        if icp.get("industry"):
            parts.append(icp["industry"])
        parts.extend(icp.get("keywords", []) or [])
        if icp.get("geography"):
            parts.append(icp["geography"])
        parts.append("company")
        return " ".join(p for p in parts if p)

    def search(self, icp: dict[str, Any], max_results: int) -> list[dict[str, Any]]:
        if not settings.google_cse_api_key or not settings.google_cse_engine_id:
            return MockSource().search(icp, max_results)

        params = {
            "key": settings.google_cse_api_key,
            "cx": settings.google_cse_engine_id,
            "q": self._query_for(icp),
            "num": min(max_results, 10),
        }
        try:
            resp = httpx.get(self.endpoint, params=params, timeout=15.0)
            resp.raise_for_status()
            items = resp.json().get("items", [])
        except Exception:
            return MockSource().search(icp, max_results)

        prospects: list[dict[str, Any]] = []
        for it in items[:max_results]:
            domain = urlparse(it.get("link", "")).netloc
            prospects.append(
                {
                    "company_name": it.get("title", domain).split(" - ")[0].strip(),
                    "website": it.get("link"),
                    "industry": icp.get("industry"),
                    "description": it.get("snippet", ""),
                    "tags": list(icp.get("keywords") or []),
                    "source": "google_cse",
                }
            )
        return prospects
