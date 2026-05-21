"""Pluggable discovery sources.

A source maps an ICP to a list of candidate prospect dicts. The active source
is chosen by `DISCOVERY_SOURCE` env var. Sources gracefully fall back to the
mock pool when their API keys are missing or calls fail.
"""
from __future__ import annotations

from .base import DiscoverySource
from .composite import CompositeSource
from .google_cse_source import GoogleCSESource
from .hunter_source import HunterSource
from .mock_source import MockSource


def get_source(name: str | None = None) -> DiscoverySource:
    """Return a source by name. Defaults to mock if name is unknown/missing."""
    name = (name or "mock").lower()
    if name == "google_cse":
        return GoogleCSESource()
    if name == "hunter":
        return HunterSource()
    if name == "composite":
        return CompositeSource([GoogleCSESource(), HunterSource(), MockSource()])
    return MockSource()


__all__ = ["DiscoverySource", "get_source"]
