"""Outreach mailer.

Pluggable provider (mock | resend). The mock provider just records that an
email "would have been sent" so the pipeline runs end-to-end with no keys.
Resend uses the official SDK if `RESEND_API_KEY` is set.

Each `send` returns a dict with at least: provider, message_id, status.
"""
from __future__ import annotations

import uuid
from typing import Any

from .config import settings


def parse_email(raw: str) -> tuple[str, str]:
    """Split the agent's `Subject: ...\\n\\nBody...` format into (subject, body)."""
    if not raw:
        return ("(no subject)", "")
    text = raw.strip()
    if text.lower().startswith("subject:"):
        head, _, rest = text.partition("\n")
        subject = head.split(":", 1)[1].strip()
        return subject, rest.lstrip("\n")
    return ("(no subject)", text)


class Mailer:
    """Provider-agnostic outreach sender."""

    def __init__(self) -> None:
        self.provider = settings.mailer_provider.lower()
        self._resend = None
        if self.provider == "resend" and settings.resend_api_key:
            try:
                import resend

                resend.api_key = settings.resend_api_key
                self._resend = resend
            except Exception:
                self.provider = "mock"
        elif self.provider == "resend":
            self.provider = "mock"

    def send(self, *, to_email: str, to_name: str | None, subject: str, body: str) -> dict[str, Any]:
        from_addr = (
            f"{settings.outreach_from_name} <{settings.outreach_from_email}>"
            if settings.outreach_from_name
            else settings.outreach_from_email
        )
        to_addr = f"{to_name} <{to_email}>" if to_name else to_email

        if self._resend is not None:
            try:
                resp = self._resend.Emails.send(
                    {
                        "from": from_addr,
                        "to": [to_addr],
                        "subject": subject,
                        "text": body,
                    }
                )
                return {
                    "provider": "resend",
                    "message_id": resp.get("id") if isinstance(resp, dict) else getattr(resp, "id", None),
                    "status": "queued",
                }
            except Exception as e:
                return {"provider": "resend", "message_id": None, "status": "error", "error": str(e)}

        # Mock provider
        return {
            "provider": "mock",
            "message_id": f"mock-{uuid.uuid4().hex[:12]}",
            "status": "queued",
        }


mailer = Mailer()
