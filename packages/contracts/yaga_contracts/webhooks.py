"""Webhook callback DTOs and header constants."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

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

    @model_validator(mode="after")
    def _check_status_dependent_fields(self) -> PublicationStatusWebhook:
        if self.status == "published" and self.published_at is None:
            msg = "published_at is required when status is 'published'"
            raise ValueError(msg)
        if self.status == "failed" and self.failure_reason is None:
            msg = "failure_reason is required when status is 'failed'"
            raise ValueError(msg)
        return self
