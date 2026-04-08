"""Webhook callback DTOs and header constants."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from yaga_contracts.shared import PublishStatus

# ── Constants ────────────────────────────────────────────────────────

WEBHOOK_SIGNATURE_HEADER = "X-Yaga-Signature"
WEBHOOK_TIMESTAMP_HEADER = "X-Yaga-Timestamp"
WEBHOOK_EVENT_ID_HEADER = "X-Yaga-Event-Id"
WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS = 300

# ── DTOs ─────────────────────────────────────────────────────────────


class PublicationStatusWebhook(BaseModel):
    """Webhook payload sent when a publication status changes."""

    model_config = ConfigDict(frozen=True)

    event_id: str
    request_id: str
    publication_id: str
    publish_dedup_key: str
    status: PublishStatus
    channel: str
    session_key: str
    published_at: datetime | None = None
    failure_reason: str | None = None
