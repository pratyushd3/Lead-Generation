"""DiscoverySource interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DiscoverySource(ABC):
    """Strategy for discovering candidate prospect companies given an ICP."""

    name: str = "base"

    @abstractmethod
    def search(self, icp: dict[str, Any], max_results: int) -> list[dict[str, Any]]:
        """Return up to `max_results` prospect dicts.

        Each dict should contain at least: company_name, website, industry,
        description, and optionally employee_count, location, tags.
        """
        raise NotImplementedError
