"""Shared enums and value objects used across all yaga_contracts schemas."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

# ── Enums ─────────────────────────────────────────────────────────────


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    VERIFY = "VERIFY"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"


class HandoffStatus(StrEnum):
    RECEIVED = "RECEIVED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class RequestStatus(StrEnum):
    RECEIVED = "RECEIVED"
    NORMALIZED = "NORMALIZED"
    DELEGATED = "DELEGATED"
    AWAITING_CALLBACK = "AWAITING_CALLBACK"
    REPLY_PENDING = "REPLY_PENDING"
    REPLY_PUBLISHED = "REPLY_PUBLISHED"
    REPLY_FAILED = "REPLY_FAILED"
    FALLBACK_REQUIRED = "FALLBACK_REQUIRED"
    CLOSED = "CLOSED"


class PublishStatus(StrEnum):
    PENDING = "PENDING"
    ATTEMPTED = "ATTEMPTED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    FALLBACK_REQUIRED = "FALLBACK_REQUIRED"
    ABANDONED = "ABANDONED"


class RequestClass(StrEnum):
    SESSION_BOUND = "SESSION_BOUND"
    DURABLE = "DURABLE"


class ExecutionMode(StrEnum):
    SESSION_BOUND = "SESSION_BOUND"
    DETACHED = "DETACHED"


class HandoffResolution(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class TaskOutcome(StrEnum):
    DONE = "DONE"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class JobStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CommandStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"


class OutboxStatus(StrEnum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"


# ── Value Objects ─────────────────────────────────────────────────────


class Actor(BaseModel):
    """Identifies who performed an action (agent, runtime, or adapter)."""

    model_config = ConfigDict(frozen=True)

    type: str
    id: str


class ReplyTarget(BaseModel):
    """Where a reply should be delivered."""

    model_config = ConfigDict(frozen=True)

    channel: str
    session_key: str
    adapter_metadata: dict[str, Any] | None = None
