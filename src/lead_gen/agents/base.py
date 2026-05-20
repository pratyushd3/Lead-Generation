"""Base agent class - thin wrapper for naming/logging consistency."""
from __future__ import annotations

import logging

logger = logging.getLogger("lead_gen.agents")


class Agent:
    name: str = "agent"

    def log(self, msg: str) -> None:
        logger.info("[%s] %s", self.name, msg)
