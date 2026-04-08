"""Event envelope and typed payload models for the YagaAi event bus."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from yaga_contracts.shared import (
    Actor,
    HandoffStatus,
    PublishStatus,
    ReplyTarget,
    RequestClass,
    TaskOutcome,
    TaskStatus,
)

# ── Event Envelope ───────────────────────────────────────────────────


class EventEnvelope(BaseModel):
    """Immutable wrapper carried by every domain event on the bus."""

    model_config = ConfigDict(frozen=True)

    event_id: str
    dedup_key: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    correlation_id: str
    causation_id: str | None = None
    actor: Actor
    occurred_at: datetime
    schema_version: str = "v1"
    stream_sequence: int
    payload: dict[str, Any]


# ── Typed Payload Models ─────────────────────────────────────────────


class RequestReceivedPayload(BaseModel):
    """Payload for a newly received external request."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    origin: str
    origin_session_key: str | None = None
    idempotency_key: str
    request_class: RequestClass
    reply_target: ReplyTarget | None = None


class RequestNormalizationPayload(BaseModel):
    """Payload emitted after a request is normalized and routed."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    strategic_owner_agent_id: str
    default_assignee_agent_id: str


class TaskLifecyclePayload(BaseModel):
    """Payload for task state transitions."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    request_id: str | None = None
    owner_agent_id: str
    status: TaskStatus
    outcome: TaskOutcome | None = None


class HandoffLifecyclePayload(BaseModel):
    """Payload for handoff state transitions."""

    model_config = ConfigDict(frozen=True)

    handoff_id: str
    task_id: str
    from_agent: str
    to_agent: str
    status: HandoffStatus
    reason: str | None = None


class CallbackPayload(BaseModel):
    """Payload for task-completion callbacks between agents."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    callback_target: str
    outcome: TaskOutcome
    source_agent_id: str
    target_agent_id: str
    result_summary: str | None = None


class PublicationPayload(BaseModel):
    """Payload for reply-publication lifecycle events."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    publish_dedup_key: str
    status: PublishStatus
    channel: str | None = None
    session_key: str | None = None


class WatchdogPayload(BaseModel):
    """Payload for watchdog / scheduled-job events."""

    model_config = ConfigDict(frozen=True)

    job_id: str
    job_type: str
    subject_type: str
    subject_id: str


class CommandRejectedPayload(BaseModel):
    """Payload emitted when a command is rejected by the runtime."""

    model_config = ConfigDict(frozen=True)

    command_type: str
    reason: str
