"""Outreach agent: lead + ICP -> personalized email + follow-up draft."""
from __future__ import annotations

from typing import Any

from ..llm import llm
from .base import Agent


class OutreachAgent(Agent):
    name = "outreach"

    def draft(self, lead: dict[str, Any], icp: dict[str, Any], buyer: dict[str, Any]) -> dict[str, str]:
        self.log(f"drafting outreach to {lead.get('contact_name')} @ {lead.get('company_name')}")
        contact = lead.get("contact_name") or "there"
        company = lead.get("company_name", "your team")
        sender = buyer.get("name", "our team")
        signals = ", ".join(lead.get("buying_signals", []) or []) or "your recent growth"

        fallback_email = (
            f"Subject: Quick idea for {company}\n\n"
            f"Hi {contact},\n\n"
            f"Noticed {signals} — congrats. Many {icp.get('industry', 'companies')} like {company} "
            f"hit a wall around {icp.get('pain_points', 'scaling operations')}. "
            f"We've helped similar teams get past it; happy to share a 2-minute teardown if useful.\n\n"
            f"Worth a 15-min chat next week?\n\n"
            f"— {sender}"
        )
        fallback_followup = (
            f"Subject: Re: Quick idea for {company}\n\n"
            f"Hi {contact},\n\nBumping this up — happy to send the teardown over async if a "
            f"call doesn't fit. Either way, no pressure.\n\n— {sender}"
        )

        result = llm.complete_json(
            system=(
                "You are a B2B SDR copywriter. Write a personalized cold email and a short "
                "follow-up. Return JSON {\"email\": str, \"followup\": str}. Each must include "
                "a Subject line. Keep email under 90 words, reference one concrete signal, "
                "tie it to the ICP's pain point, end with a single soft CTA."
            ),
            user=f"BUYER: {buyer}\nICP: {icp}\nLEAD: {lead}",
            fallback={"email": fallback_email, "followup": fallback_followup},
        )
        return {
            "email": result.get("email", fallback_email),
            "followup": result.get("followup", fallback_followup),
        }
