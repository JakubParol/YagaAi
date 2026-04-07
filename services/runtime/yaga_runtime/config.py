"""Runtime configuration model for the kickoff slice."""

import secrets
from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_RUNTIME_DIR = Path(__file__).resolve().parent.parent


class EnvironmentMode(StrEnum):
    """Runtime environment mode."""

    LOCAL_DEV = "local-dev"
    PROD = "prod"


class RuntimeSettings(BaseSettings):
    """Centralized configuration for the YagaAi runtime daemon.

    All kickoff-critical settings live here. Values can be overridden
    via environment variables or a `.env` file.
    """

    model_config = SettingsConfigDict(
        env_prefix="YAGA_",
        env_file=_RUNTIME_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Environment ---
    env: EnvironmentMode = EnvironmentMode.LOCAL_DEV

    # --- Database ---
    sqlite_path: Path = Path("yaga.db")

    # --- Auth ---
    bootstrap_bearer_token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
    )

    # --- Webhooks ---
    webhook_signing_secret: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
    )

    # --- Agents ---
    default_assignee_agent_id: str = "naomi"

    @property
    def database_url(self) -> str:
        """SQLAlchemy-compatible async database URL."""
        return f"sqlite+aiosqlite:///{self.sqlite_path}"
