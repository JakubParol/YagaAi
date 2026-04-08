"""Internal command models for the YagaAi runtime."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from yaga_contracts.http import RequestPayload
from yaga_contracts.shared import (
    Actor,
    ExecutionMode,
    PublishStatus,
    ReplyTarget,
    RequestClass,
    TaskOutcome,
)

# ── Base ─────────────────────────────────────────────────────────────


class CommandBase(BaseModel):
    """Immutable base class shared by every internal command."""

    model_config = ConfigDict(frozen=True)

    command_id: str
    command_type: str
    aggregate_type: str
    aggregate_id: str
    correlation_id: str
    causation_id: str | None = None
    dedup_key: str
    occurred_at: datetime
    actor: Actor
    schema_version: str = "v1"


# ── Concrete Commands ────────────────────────────────────────────────


class AcceptRequestCommand(CommandBase):
    """Accept an inbound request from an external adapter."""

    command_type: Literal["accept_request"] = "accept_request"

    request_id: str
    idempotency_key: str
    origin: str
    origin_session_key: str | None = None
    request_class: RequestClass
    reply_target: ReplyTarget | None = None
    payload: RequestPayload


class CreateTaskCommand(CommandBase):
    """Create a new task for an agent to work on."""

    command_type: Literal["create_task"] = "create_task"

    task_id: str
    request_id: str
    owner_agent: str
    callback_target: str


class DispatchHandoffCommand(CommandBase):
    """Dispatch a handoff from one agent to another."""

    command_type: Literal["dispatch_handoff"] = "dispatch_handoff"

    handoff_id: str
    task_id: str
    request_id: str | None = None
    from_agent: str
    to_agent: str
    goal: str
    definition_of_done: str
    callback_target: str
    execution_mode: ExecutionMode


class AcceptHandoffCommand(CommandBase):
    """Record that an agent accepted a handoff."""

    command_type: Literal["accept_handoff"] = "accept_handoff"

    handoff_id: str
    task_id: str
    responder_agent: str


class RejectHandoffCommand(CommandBase):
    """Record that an agent rejected a handoff."""

    command_type: Literal["reject_handoff"] = "reject_handoff"

    handoff_id: str
    task_id: str
    responder_agent: str
    reason: str


class CompleteTaskCommand(CommandBase):
    """Mark a task as completed."""

    command_type: Literal["complete_task"] = "complete_task"

    task_id: str
    request_id: str | None = None
    outcome: TaskOutcome
    result_summary: str | None = None
    completed_by_agent: str


class RecordPublicationAttemptCommand(CommandBase):
    """Record that a reply publication was attempted."""

    command_type: Literal["record_publication_attempt"] = "record_publication_attempt"

    publication_id: str
    request_id: str
    publish_dedup_key: str
    channel: str
    session_key: str


class RecordPublicationResultCommand(CommandBase):
    """Record the outcome of a reply publication attempt."""

    command_type: Literal["record_publication_result"] = "record_publication_result"

    publication_id: str
    request_id: str
    webhook_event_id: str
    status: PublishStatus
    failure_reason: str | None = None


class ScheduleJobCommand(CommandBase):
    """Schedule a deferred job for future execution."""

    command_type: Literal["schedule_job"] = "schedule_job"

    job_id: str
    job_type: str
    subject_type: str
    subject_id: str
    run_at: datetime
    payload_json: dict[str, Any] | None = None


class CancelJobCommand(CommandBase):
    """Cancel a previously scheduled job."""

    command_type: Literal["cancel_job"] = "cancel_job"

    job_id: str
