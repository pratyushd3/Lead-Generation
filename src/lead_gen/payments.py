"""Payments provider abstraction.

  - "mock"   instant-success local-only "checkout" (default, no API key needed)
  - "stripe" real Stripe Checkout Sessions; completion handled via webhook
"""
from __future__ import annotations

import uuid
from typing import Any

from .config import settings


class Payments:
    def __init__(self) -> None:
        self.provider = settings.payments_provider.lower()
        self._stripe = None
        if self.provider == "stripe" and settings.stripe_api_key:
            try:
                import stripe

                stripe.api_key = settings.stripe_api_key
                self._stripe = stripe
            except Exception:
                self.provider = "mock"
        elif self.provider == "stripe":
            self.provider = "mock"

    def create_checkout(
        self,
        *,
        order_id: int,
        lead_company: str,
        amount_cents: int,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict[str, Any]:
        """Create a checkout session. Returns {provider, session_id, url, status}."""
        success_url = success_url or settings.marketplace_success_url
        cancel_url = cancel_url or settings.marketplace_cancel_url

        if self._stripe is not None:
            try:
                session = self._stripe.checkout.Session.create(
                    mode="payment",
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "unit_amount": amount_cents,
                                "product_data": {
                                    "name": f"Lead: {lead_company}",
                                    "description": "Qualified B2B lead with outreach drafts",
                                },
                            },
                            "quantity": 1,
                        }
                    ],
                    success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=cancel_url,
                    metadata={"order_id": str(order_id)},
                )
                return {
                    "provider": "stripe",
                    "session_id": session["id"],
                    "url": session["url"],
                    "status": "pending",
                }
            except Exception as e:
                return {"provider": "stripe", "session_id": None, "url": None, "status": "error", "error": str(e)}

        # Mock provider: instant success.
        session_id = f"mock-cs-{uuid.uuid4().hex[:12]}"
        return {
            "provider": "mock",
            "session_id": session_id,
            "url": f"{success_url}?session_id={session_id}&order_id={order_id}",
            "status": "paid",
        }

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict[str, Any] | None:
        """Verify a Stripe webhook signature and return the parsed event, or None."""
        if self._stripe is None or not settings.stripe_webhook_secret:
            return None
        try:
            event = self._stripe.Webhook.construct_event(
                payload, signature or "", settings.stripe_webhook_secret
            )
            return event
        except Exception:
            return None


payments = Payments()
