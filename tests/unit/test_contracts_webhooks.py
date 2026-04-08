"""Tests for yaga_contracts.webhooks — webhook callback DTOs and constants."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, cast

import pytest
from pydantic import ValidationError

from yaga_contracts.shared import PublishStatus
from yaga_contracts.webhooks import (
    WEBHOOK_EVENT_ID_HEADER,
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_TIMESTAMP_HEADER,
    WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS,
    PublicationStatusWebhook,
)

# ── PublicationStatusWebhook ────────────────────────────────────────


class TestPublicationStatusWebhook:
    def _make(self, **overrides: Any) -> PublicationStatusWebhook:
        defaults: dict[str, Any] = {
            "event_id": "evt-001",
            "request_id": "req-001",
            "publication_id": "pub-001",
            "publish_dedup_key": "dedup-001",
            "status": PublishStatus.PUBLISHED,
            "channel": "slack",
            "session_key": "sess-001",
            "published_at": datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC),
            "failure_reason": None,
        }
        defaults.update(overrides)
        return PublicationStatusWebhook(**defaults)

    def test_published_webhook(self) -> None:
        wh = self._make(
            status=PublishStatus.PUBLISHED,
            published_at=datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC),
            failure_reason=None,
        )
        assert wh.status == PublishStatus.PUBLISHED
        assert wh.published_at == datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC)
        assert wh.failure_reason is None

    def test_failed_webhook(self) -> None:
        wh = self._make(
            status=PublishStatus.FAILED,
            failure_reason="timeout",
            published_at=None,
        )
        assert wh.status == PublishStatus.FAILED
        assert wh.failure_reason == "timeout"
        assert wh.published_at is None

    def test_frozen(self) -> None:
        wh = self._make()
        with pytest.raises(ValidationError):
            cast(Any, wh).status = PublishStatus.FAILED

    def test_json_wire_format(self) -> None:
        wh = self._make(
            event_id="evt-wire",
            request_id="req-wire",
            publication_id="pub-wire",
            publish_dedup_key="dedup-wire",
            status=PublishStatus.PUBLISHED,
            channel="slack",
            session_key="sess-wire",
            published_at=datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC),
            failure_reason=None,
        )
        data: dict[str, Any] = json.loads(wh.model_dump_json())
        assert set(data.keys()) == {
            "event_id",
            "request_id",
            "publication_id",
            "publish_dedup_key",
            "status",
            "channel",
            "session_key",
            "published_at",
            "failure_reason",
        }
        assert data["event_id"] == "evt-wire"
        assert data["status"] == "PUBLISHED"
        assert data["failure_reason"] is None


# ── Header constants ────────────────────────────────────────────────


class TestWebhookConstants:
    def test_signature_header(self) -> None:
        assert WEBHOOK_SIGNATURE_HEADER == "X-Yaga-Signature"

    def test_timestamp_header(self) -> None:
        assert WEBHOOK_TIMESTAMP_HEADER == "X-Yaga-Timestamp"

    def test_event_id_header(self) -> None:
        assert WEBHOOK_EVENT_ID_HEADER == "X-Yaga-Event-Id"

    def test_timestamp_tolerance(self) -> None:
        assert WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS == 300
