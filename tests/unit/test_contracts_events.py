"""Tests for yaga_contracts.events — event envelope and typed payloads."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from yaga_contracts.events import (
    CallbackPayload,
    CommandRejectedPayload,
    EventEnvelope,
    HandoffLifecyclePayload,
    PublicationPayload,
    RequestNormalizationPayload,
    RequestReceivedPayload,
    TaskLifecyclePayload,
    WatchdogPayload,
)
from yaga_contracts.shared import (
    Actor,
    HandoffStatus,
    PublishStatus,
    ReplyTarget,
    RequestClass,
    TaskOutcome,
    TaskStatus,
)

# ── Helpers ──────────────────────────────────────────────────────────

_NOW = datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC)
_ACTOR = Actor(type="agent", id="james-001")


def _envelope_kwargs(**overrides: Any) -> dict[str, Any]:
    """Return a complete set of kwargs for EventEnvelope."""
    base: dict[str, Any] = {
        "event_id": "evt-1",
        "dedup_key": "dedup-1",
        "event_type": "request.received",
        "aggregate_type": "request",
        "aggregate_id": "req-1",
        "correlation_id": "corr-1",
        "actor": _ACTOR,
        "occurred_at": _NOW,
        "stream_sequence": 1,
        "payload": {"request_id": "req-1"},
    }
    base.update(overrides)
    return base


# ── EventEnvelope ────────────────────────────────────────────────────


class TestEventEnvelope:
    def test_creation_all_fields(self) -> None:
        env = EventEnvelope(**_envelope_kwargs(causation_id="cause-1"))
        assert env.event_id == "evt-1"
        assert env.dedup_key == "dedup-1"
        assert env.event_type == "request.received"
        assert env.aggregate_type == "request"
        assert env.aggregate_id == "req-1"
        assert env.correlation_id == "corr-1"
        assert env.causation_id == "cause-1"
        assert env.actor == _ACTOR
        assert env.occurred_at == _NOW
        assert env.schema_version == "v1"
        assert env.stream_sequence == 1
        assert env.payload == {"request_id": "req-1"}

    def test_causation_id_optional_on_root_events(self) -> None:
        env = EventEnvelope(**_envelope_kwargs())
        assert env.causation_id is None

    def test_schema_version_defaults_to_v1(self) -> None:
        env = EventEnvelope(**_envelope_kwargs())
        assert env.schema_version == "v1"

    def test_stream_sequence_required(self) -> None:
        kwargs = _envelope_kwargs()
        del kwargs["stream_sequence"]
        with pytest.raises(ValidationError):
            EventEnvelope(**kwargs)

    def test_frozen(self) -> None:
        env = EventEnvelope(**_envelope_kwargs())
        with pytest.raises(Exception):  # noqa: B017
            env.event_id = "changed"  # type: ignore[misc]

    def test_json_round_trip(self) -> None:
        env = EventEnvelope(**_envelope_kwargs(causation_id="cause-1"))
        data: dict[str, Any] = json.loads(env.model_dump_json())
        restored = EventEnvelope.model_validate(data)
        assert restored == env

    def test_payload_dict_round_trip(self) -> None:
        env = EventEnvelope(**_envelope_kwargs())
        data = env.model_dump()
        restored = EventEnvelope.model_validate(data)
        assert restored == env


# ── RequestReceivedPayload ───────────────────────────────────────────


class TestRequestReceivedPayload:
    def test_creation_minimal(self) -> None:
        p = RequestReceivedPayload(
            request_id="req-1",
            origin="slack",
            idempotency_key="idem-1",
            request_class=RequestClass.SESSION_BOUND,
        )
        assert p.request_id == "req-1"
        assert p.origin == "slack"
        assert p.origin_session_key is None
        assert p.idempotency_key == "idem-1"
        assert p.request_class == RequestClass.SESSION_BOUND
        assert p.reply_target is None

    def test_creation_full(self) -> None:
        rt = ReplyTarget(channel="slack", session_key="sess-1")
        p = RequestReceivedPayload(
            request_id="req-1",
            origin="slack",
            origin_session_key="sess-1",
            idempotency_key="idem-1",
            request_class=RequestClass.DURABLE,
            reply_target=rt,
        )
        assert p.origin_session_key == "sess-1"
        assert p.reply_target == rt

    def test_frozen(self) -> None:
        p = RequestReceivedPayload(
            request_id="req-1",
            origin="slack",
            idempotency_key="idem-1",
            request_class=RequestClass.SESSION_BOUND,
        )
        with pytest.raises(Exception):  # noqa: B017
            p.request_id = "changed"  # type: ignore[misc]


# ── RequestNormalizationPayload ──────────────────────────────────────


class TestRequestNormalizationPayload:
    def test_creation(self) -> None:
        p = RequestNormalizationPayload(
            request_id="req-1",
            strategic_owner_agent_id="james-001",
            default_assignee_agent_id="naomi-001",
        )
        assert p.request_id == "req-1"
        assert p.strategic_owner_agent_id == "james-001"
        assert p.default_assignee_agent_id == "naomi-001"


# ── TaskLifecyclePayload ────────────────────────────────────────────


class TestTaskLifecyclePayload:
    def test_creation_without_outcome(self) -> None:
        p = TaskLifecyclePayload(
            task_id="task-1",
            request_id="req-1",
            owner_agent_id="james-001",
            status=TaskStatus.CREATED,
        )
        assert p.task_id == "task-1"
        assert p.request_id == "req-1"
        assert p.owner_agent_id == "james-001"
        assert p.status == TaskStatus.CREATED
        assert p.outcome is None

    def test_creation_with_outcome(self) -> None:
        p = TaskLifecyclePayload(
            task_id="task-1",
            owner_agent_id="james-001",
            status=TaskStatus.DONE,
            outcome=TaskOutcome.DONE,
        )
        assert p.outcome == TaskOutcome.DONE
        assert p.request_id is None


# ── HandoffLifecyclePayload ─────────────────────────────────────────


class TestHandoffLifecyclePayload:
    def test_creation(self) -> None:
        p = HandoffLifecyclePayload(
            handoff_id="ho-1",
            task_id="task-1",
            from_agent="james-001",
            to_agent="naomi-001",
            status=HandoffStatus.RECEIVED,
        )
        assert p.handoff_id == "ho-1"
        assert p.reason is None

    def test_creation_with_reason(self) -> None:
        p = HandoffLifecyclePayload(
            handoff_id="ho-1",
            task_id="task-1",
            from_agent="james-001",
            to_agent="naomi-001",
            status=HandoffStatus.REJECTED,
            reason="Not my area",
        )
        assert p.reason == "Not my area"


# ── CallbackPayload ─────────────────────────────────────────────────


class TestCallbackPayload:
    def test_creation(self) -> None:
        p = CallbackPayload(
            task_id="task-1",
            callback_target="target-1",
            outcome=TaskOutcome.DONE,
            source_agent_id="naomi-001",
            target_agent_id="james-001",
        )
        assert p.task_id == "task-1"
        assert p.callback_target == "target-1"
        assert p.outcome == TaskOutcome.DONE
        assert p.source_agent_id == "naomi-001"
        assert p.target_agent_id == "james-001"
        assert p.result_summary is None

    def test_creation_with_summary(self) -> None:
        p = CallbackPayload(
            task_id="task-1",
            callback_target="target-1",
            outcome=TaskOutcome.FAILED,
            source_agent_id="naomi-001",
            target_agent_id="james-001",
            result_summary="Something went wrong",
        )
        assert p.result_summary == "Something went wrong"


# ── PublicationPayload ───────────────────────────────────────────────


class TestPublicationPayload:
    def test_creation(self) -> None:
        p = PublicationPayload(
            request_id="req-1",
            publish_dedup_key="pub-dedup-1",
            status=PublishStatus.PUBLISHED,
        )
        assert p.request_id == "req-1"
        assert p.channel is None
        assert p.session_key is None

    def test_creation_full(self) -> None:
        p = PublicationPayload(
            request_id="req-1",
            publish_dedup_key="pub-dedup-1",
            status=PublishStatus.PUBLISHED,
            channel="slack",
            session_key="sess-1",
        )
        assert p.channel == "slack"
        assert p.session_key == "sess-1"


# ── WatchdogPayload ─────────────────────────────────────────────────


class TestWatchdogPayload:
    def test_creation(self) -> None:
        p = WatchdogPayload(
            job_id="job-1",
            job_type="timeout_check",
            subject_type="task",
            subject_id="task-1",
        )
        assert p.job_id == "job-1"
        assert p.job_type == "timeout_check"
        assert p.subject_type == "task"
        assert p.subject_id == "task-1"


# ── CommandRejectedPayload ──────────────────────────────────────────


class TestCommandRejectedPayload:
    def test_creation(self) -> None:
        p = CommandRejectedPayload(
            command_type="assign_task",
            reason="Agent not available",
        )
        assert p.command_type == "assign_task"
        assert p.reason == "Agent not available"
