"""Application configuration loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    llm_provider: str = "mock"  # "mock" | "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""

    # Storage
    database_url: str = "sqlite:///./leadgen.db"

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000


settings = Settings()
