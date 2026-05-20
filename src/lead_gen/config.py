"""Application configuration loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    llm_provider: str = "mock"  # "mock" | "openai" | "anthropic"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Discovery sources
    discovery_source: str = "mock"  # "mock" | "google_cse" | "hunter" | "composite"
    google_cse_api_key: str = ""
    google_cse_engine_id: str = ""
    hunter_api_key: str = ""

    # Outreach mailer
    mailer_provider: str = "mock"  # "mock" | "resend"
    resend_api_key: str = ""
    outreach_from_email: str = "noreply@example.com"
    outreach_from_name: str = "Lead Gen Agency"

    # Marketplace payments
    payments_provider: str = "mock"  # "mock" | "stripe"
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    marketplace_success_url: str = "http://localhost:3000/marketplace/success"
    marketplace_cancel_url: str = "http://localhost:3000/marketplace"

    # Storage
    database_url: str = "sqlite:///./leadgen.db"

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # CORS for the dashboard
    cors_origins: str = "http://localhost:3000"


settings = Settings()
