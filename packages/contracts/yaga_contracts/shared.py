"""Shared enums and value objects used across all yaga_contracts schemas."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

# ── Enums ─────────────────────────────────────────────────────────────


class TaskStatus(StrEnum):
    CREATED = "Created"
    ACCEPTED = "Accepted"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    VERIFY = "Verify"
    DONE = "Done"
    BLOCKED = "Blocked"
    ESCALATED = "Escalated"
    CANCELLED = "Cancelled"


class HandoffStatus(StrEnum):
    RECEIVED = "received"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RequestStatus(StrEnum):
    RECEIVED = "received"
    NORMALIZED = "normalized"
    DELEGATED = "delegated"
    AWAITING_CALLBACK = "awaiting_callback"
    REPLY_PENDING = "reply_pending"
    REPLY_PUBLISHED = "reply_published"
    REPLY_FAILED = "reply_failed"
    FALLBACK_REQUIRED = "fallback_required"
    CLOSED = "closed"


class PublishStatus(StrEnum):
    PENDING = "pending"
    ATTEMPTED = "attempted"
    PUBLISHED = "published"
    FAILED = "failed"
    UNKNOWN = "unknown"
    FALLBACK_REQUIRED = "fallback_required"
    ABANDONED = "abandoned"


class RequestClass(StrEnum):
    SESSION_BOUND = "session_bound"
    DURABLE = "durable"


class ExecutionMode(StrEnum):
    SESSION_BOUND = "session_bound"
    DETACHED = "detached"


class HandoffResolution(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TaskOutcome(StrEnum):
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class JobStatus(StrEnum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PROCESSED = "processed"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    FAILED = "failed"


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
