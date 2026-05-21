"""Hunter.io discovery source.

Uses the Hunter `domain-search` for keyword/industry combinations to surface
companies and their associated emails. Requires HUNTER_API_KEY. Falls back
to the mock source when missing or on failure.
"""
from __future__ import annotations

from typing import Any

import httpx

from ..config import settings
from .base import DiscoverySource
from .mock_source import MockSource


class HunterSource(DiscoverySource):
    name = "hunter"
    endpoint = "https://api.hunter.io/v2/domain-search"

    def search(self, icp: dict[str, Any], max_results: int) -> list[dict[str, Any]]:
        if not settings.hunter_api_key:
            return MockSource().search(icp, max_results)

        # Hunter is per-domain; we round-robin a list of seed domains derived
        # from keywords. In production you'd pair this with a discovery API
        # that returns domains first (Apollo, BuiltWith, etc.).
        seeds = [k.replace(" ", "") + ".com" for k in (icp.get("keywords") or [])][:max_results]
        if not seeds:
            return MockSource().search(icp, max_results)

        results: list[dict[str, Any]] = []
        for domain in seeds:
            try:
                resp = httpx.get(
                    self.endpoint,
                    params={"domain": domain, "api_key": settings.hunter_api_key, "limit": 1},
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
            except Exception:
                continue

            if not data.get("organization"):
                continue
            email = (data.get("emails") or [{}])[0]
            results.append(
                {
                    "company_name": data.get("organization"),
                    "website": f"https://{domain}",
                    "industry": data.get("industry") or icp.get("industry"),
                    "employee_count": None,
                    "location": ", ".join(filter(None, [data.get("city"), data.get("country")])),
                    "description": data.get("description", ""),
                    "tags": data.get("technologies", []) or list(icp.get("keywords") or []),
                    "contact_name": (
                        f"{email.get('first_name', '')} {email.get('last_name', '')}".strip() or None
                    ),
                    "contact_title": email.get("position"),
                    "contact_email": email.get("value"),
                    "source": "hunter",
                }
            )
            if len(results) >= max_results:
                break

        return results or MockSource().search(icp, max_results)
