"""Tests for RuntimeSettings configuration model."""

import os
from pathlib import Path

from yaga_runtime.config import EnvironmentMode, RuntimeSettings


class TestRuntimeSettingsDefaults:
    def test_default_env_is_local_dev(self) -> None:
        settings = RuntimeSettings()
        assert settings.env == EnvironmentMode.LOCAL_DEV

    def test_default_sqlite_path(self) -> None:
        settings = RuntimeSettings()
        assert settings.sqlite_path == Path("yaga.db")

    def test_default_assignee_is_naomi(self) -> None:
        settings = RuntimeSettings()
        assert settings.default_assignee_agent_id == "naomi"

    def test_database_url_property(self) -> None:
        settings = RuntimeSettings()
        assert settings.database_url == "sqlite+aiosqlite:///yaga.db"

    def test_bearer_token_auto_generated(self) -> None:
        settings = RuntimeSettings()
        assert len(settings.bootstrap_bearer_token) > 0

    def test_webhook_secret_auto_generated(self) -> None:
        settings = RuntimeSettings()
        assert len(settings.webhook_signing_secret) > 0

    def test_auto_generated_secrets_are_unique(self) -> None:
        s1 = RuntimeSettings()
        s2 = RuntimeSettings()
        assert s1.bootstrap_bearer_token != s2.bootstrap_bearer_token
        assert s1.webhook_signing_secret != s2.webhook_signing_secret


class TestRuntimeSettingsEnvOverride:
    def test_env_override(self, monkeypatch: object) -> None:
        os.environ["YAGA_ENV"] = "prod"
        try:
            settings = RuntimeSettings()
            assert settings.env == EnvironmentMode.PROD
        finally:
            del os.environ["YAGA_ENV"]

    def test_sqlite_path_override(self) -> None:
        os.environ["YAGA_SQLITE_PATH"] = "/tmp/test.db"
        try:
            settings = RuntimeSettings()
            assert settings.sqlite_path == Path("/tmp/test.db")
            assert settings.database_url == "sqlite+aiosqlite:////tmp/test.db"
        finally:
            del os.environ["YAGA_SQLITE_PATH"]

    def test_bearer_token_override(self) -> None:
        os.environ["YAGA_BOOTSTRAP_BEARER_TOKEN"] = "my-token"
        try:
            settings = RuntimeSettings()
            assert settings.bootstrap_bearer_token == "my-token"
        finally:
            del os.environ["YAGA_BOOTSTRAP_BEARER_TOKEN"]

    def test_assignee_override(self) -> None:
        os.environ["YAGA_DEFAULT_ASSIGNEE_AGENT_ID"] = "amos"
        try:
            settings = RuntimeSettings()
            assert settings.default_assignee_agent_id == "amos"
        finally:
            del os.environ["YAGA_DEFAULT_ASSIGNEE_AGENT_ID"]


class TestRuntimeSettingsValidation:
    def test_invalid_env_mode_rejected(self) -> None:
        os.environ["YAGA_ENV"] = "staging"
        try:
            from pydantic import ValidationError

            raised = False
            try:
                RuntimeSettings()
            except ValidationError:
                raised = True
            assert raised, "Expected ValidationError for invalid env mode"
        finally:
            del os.environ["YAGA_ENV"]
