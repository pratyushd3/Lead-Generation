"""Provider-agnostic LLM client.

Supports three providers, selected by `LLM_PROVIDER`:
  - "mock"      deterministic stubs, no API key needed (default)
  - "openai"    requires OPENAI_API_KEY
  - "anthropic" requires ANTHROPIC_API_KEY

All methods fall back to a caller-supplied default on any error so the
pipeline never hard-fails.
"""
from __future__ import annotations

import json
from typing import Any

from .config import settings


def _default_model_for(provider: str, configured: str) -> str:
    if configured and configured != "gpt-4o-mini":
        return configured
    return {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-latest",
    }.get(provider, configured)


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()
        self.model = _default_model_for(self.provider, settings.llm_model)
        self._openai = None
        self._anthropic = None

        if self.provider == "openai" and settings.openai_api_key:
            try:
                from openai import OpenAI

                self._openai = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self.provider = "mock"
        elif self.provider == "anthropic" and settings.anthropic_api_key:
            try:
                from anthropic import Anthropic

                self._anthropic = Anthropic(api_key=settings.anthropic_api_key)
            except Exception:
                self.provider = "mock"
        elif self.provider in {"openai", "anthropic"}:
            # Configured but missing key -> degrade silently.
            self.provider = "mock"

    # ---------- public API ----------

    def complete_json(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON object response."""
        try:
            if self._openai is not None:
                return self._openai_json(system, user)
            if self._anthropic is not None:
                return self._anthropic_json(system, user)
        except Exception:
            pass
        return fallback

    def complete_text(self, system: str, user: str, fallback: str) -> str:
        try:
            if self._openai is not None:
                return self._openai_text(system, user)
            if self._anthropic is not None:
                return self._anthropic_text(system, user)
        except Exception:
            pass
        return fallback

    # ---------- OpenAI ----------

    def _openai_json(self, system: str, user: str) -> dict[str, Any]:
        resp = self._openai.chat.completions.create(  # type: ignore[union-attr]
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        return json.loads(resp.choices[0].message.content or "{}")

    def _openai_text(self, system: str, user: str) -> str:
        resp = self._openai.chat.completions.create(  # type: ignore[union-attr]
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
        )
        return resp.choices[0].message.content or ""

    # ---------- Anthropic ----------

    def _anthropic_json(self, system: str, user: str) -> dict[str, Any]:
        # Anthropic doesn't have a JSON-mode flag; we instruct + parse.
        resp = self._anthropic.messages.create(  # type: ignore[union-attr]
            model=self.model,
            system=system + "\n\nReturn ONLY a single valid JSON object. No prose.",
            max_tokens=1024,
            temperature=0.4,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")
        # Best-effort extraction of the first {...} block.
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        return json.loads(text)

    def _anthropic_text(self, system: str, user: str) -> str:
        resp = self._anthropic.messages.create(  # type: ignore[union-attr]
            model=self.model,
            system=system,
            max_tokens=1024,
            temperature=0.6,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")


llm = LLMClient()
