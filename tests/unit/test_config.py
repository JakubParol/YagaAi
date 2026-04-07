"""Tests for RuntimeSettings configuration model."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from yaga_runtime.config import EnvironmentMode, RuntimeSettings


def _settings() -> RuntimeSettings:
    """Create settings isolated from real .env files."""
    return RuntimeSettings(_env_file=None)


class TestRuntimeSettingsDefaults:
    def test_default_env_is_local_dev(self) -> None:
        assert _settings().env == EnvironmentMode.LOCAL_DEV

    def test_default_sqlite_path(self) -> None:
        assert _settings().sqlite_path == Path("yaga.db")

    def test_default_assignee_is_naomi(self) -> None:
        assert _settings().default_assignee_agent_id == "naomi"

    def test_database_url_property(self) -> None:
        assert _settings().database_url == "sqlite+aiosqlite:///yaga.db"

    def test_bearer_token_auto_generated(self) -> None:
        assert len(_settings().bootstrap_bearer_token) > 0

    def test_webhook_secret_auto_generated(self) -> None:
        assert len(_settings().webhook_signing_secret) > 0

    def test_auto_generated_secrets_are_unique(self) -> None:
        s1, s2 = _settings(), _settings()
        assert s1.bootstrap_bearer_token != s2.bootstrap_bearer_token
        assert s1.webhook_signing_secret != s2.webhook_signing_secret


class TestRuntimeSettingsEnvOverride:
    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_ENV", "prod")
        assert RuntimeSettings(_env_file=None).env == EnvironmentMode.PROD

    def test_sqlite_path_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_SQLITE_PATH", "/tmp/test.db")
        settings = RuntimeSettings(_env_file=None)
        assert settings.sqlite_path == Path("/tmp/test.db")
        assert settings.database_url == "sqlite+aiosqlite:////tmp/test.db"

    def test_bearer_token_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_BOOTSTRAP_BEARER_TOKEN", "my-token")
        assert RuntimeSettings(_env_file=None).bootstrap_bearer_token == "my-token"

    def test_webhook_secret_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_WEBHOOK_SIGNING_SECRET", "my-secret")
        assert RuntimeSettings(_env_file=None).webhook_signing_secret == "my-secret"

    def test_assignee_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_DEFAULT_ASSIGNEE_AGENT_ID", "amos")
        assert RuntimeSettings(_env_file=None).default_assignee_agent_id == "amos"


class TestRuntimeSettingsValidation:
    def test_invalid_env_mode_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YAGA_ENV", "staging")
        with pytest.raises(ValidationError):
            RuntimeSettings(_env_file=None)
