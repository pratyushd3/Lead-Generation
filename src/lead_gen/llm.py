"""Provider-agnostic LLM client. Supports `mock` (deterministic) and `openai`."""
from __future__ import annotations

import json
from typing import Any

from .config import settings


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model
        self._openai = None
        if self.provider == "openai":
            try:
                from openai import OpenAI

                self._openai = OpenAI(api_key=settings.openai_api_key)
            except Exception:  # pragma: no cover
                self.provider = "mock"

    def complete_json(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON object response. Falls back to `fallback` on any failure."""
        if self.provider == "openai" and self._openai is not None:
            try:
                resp = self._openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4,
                )
                return json.loads(resp.choices[0].message.content or "{}")
            except Exception:
                return fallback
        return fallback

    def complete_text(self, system: str, user: str, fallback: str) -> str:
        if self.provider == "openai" and self._openai is not None:
            try:
                resp = self._openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.6,
                )
                return resp.choices[0].message.content or fallback
            except Exception:
                return fallback
        return fallback


llm = LLMClient()
