"""Tests for yaga_contracts.shared — enums and value objects."""

from __future__ import annotations

import json
from typing import Any

import pytest

from yaga_contracts.shared import (
    Actor,
    CommandStatus,
    ExecutionMode,
    HandoffResolution,
    HandoffStatus,
    JobStatus,
    OutboxStatus,
    PublishStatus,
    ReplyTarget,
    RequestClass,
    RequestStatus,
    TaskOutcome,
    TaskStatus,
)

# ── Enum value tests ──────────────────────────────────────────────────


class TestTaskStatus:
    expected = [
        "CREATED",
        "ACCEPTED",
        "IN_PROGRESS",
        "REVIEW",
        "VERIFY",
        "DONE",
        "BLOCKED",
        "ESCALATED",
        "CANCELLED",
    ]

    def test_members(self) -> None:
        assert [m.value for m in TaskStatus] == self.expected

    def test_str_identity(self) -> None:
        assert TaskStatus.CREATED == "CREATED"


class TestHandoffStatus:
    expected = ["RECEIVED", "ACCEPTED", "REJECTED"]

    def test_members(self) -> None:
        assert [m.value for m in HandoffStatus] == self.expected

    def test_str_identity(self) -> None:
        assert HandoffStatus.RECEIVED == "RECEIVED"


class TestRequestStatus:
    expected = [
        "RECEIVED",
        "NORMALIZED",
        "DELEGATED",
        "AWAITING_CALLBACK",
        "REPLY_PENDING",
        "REPLY_PUBLISHED",
        "REPLY_FAILED",
        "FALLBACK_REQUIRED",
        "CLOSED",
    ]

    def test_members(self) -> None:
        assert [m.value for m in RequestStatus] == self.expected

    def test_str_identity(self) -> None:
        assert RequestStatus.CLOSED == "CLOSED"


class TestPublishStatus:
    expected = [
        "PENDING",
        "ATTEMPTED",
        "PUBLISHED",
        "FAILED",
        "UNKNOWN",
        "FALLBACK_REQUIRED",
        "ABANDONED",
    ]

    def test_members(self) -> None:
        assert [m.value for m in PublishStatus] == self.expected

    def test_str_identity(self) -> None:
        assert PublishStatus.PENDING == "PENDING"


class TestRequestClass:
    expected = ["SESSION_BOUND", "DURABLE"]

    def test_members(self) -> None:
        assert [m.value for m in RequestClass] == self.expected

    def test_str_identity(self) -> None:
        assert RequestClass.DURABLE == "DURABLE"


class TestExecutionMode:
    expected = ["SESSION_BOUND", "DETACHED"]

    def test_members(self) -> None:
        assert [m.value for m in ExecutionMode] == self.expected

    def test_str_identity(self) -> None:
        assert ExecutionMode.DETACHED == "DETACHED"


class TestHandoffResolution:
    expected = ["ACCEPTED", "REJECTED"]

    def test_members(self) -> None:
        assert [m.value for m in HandoffResolution] == self.expected

    def test_str_identity(self) -> None:
        assert HandoffResolution.ACCEPTED == "ACCEPTED"


class TestTaskOutcome:
    expected = ["DONE", "FAILED", "BLOCKED"]

    def test_members(self) -> None:
        assert [m.value for m in TaskOutcome] == self.expected

    def test_str_identity(self) -> None:
        assert TaskOutcome.DONE == "DONE"


class TestJobStatus:
    expected = ["SCHEDULED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]

    def test_members(self) -> None:
        assert [m.value for m in JobStatus] == self.expected

    def test_str_identity(self) -> None:
        assert JobStatus.SCHEDULED == "SCHEDULED"


class TestCommandStatus:
    expected = ["ACCEPTED", "REJECTED", "PROCESSED"]

    def test_members(self) -> None:
        assert [m.value for m in CommandStatus] == self.expected

    def test_str_identity(self) -> None:
        assert CommandStatus.PROCESSED == "PROCESSED"


class TestOutboxStatus:
    expected = ["PENDING", "DISPATCHED", "FAILED"]

    def test_members(self) -> None:
        assert [m.value for m in OutboxStatus] == self.expected

    def test_str_identity(self) -> None:
        assert OutboxStatus.DISPATCHED == "DISPATCHED"


# ── Value object tests ────────────────────────────────────────────────


class TestActor:
    def test_creation(self) -> None:
        actor = Actor(type="agent", id="james-001")
        assert actor.type == "agent"
        assert actor.id == "james-001"

    def test_frozen(self) -> None:
        actor = Actor(type="runtime", id="rt-1")
        with pytest.raises(Exception):  # noqa: B017
            actor.type = "adapter"  # type: ignore[misc]

    def test_json_round_trip(self) -> None:
        actor = Actor(type="adapter", id="slack-1")
        data: dict[str, Any] = json.loads(actor.model_dump_json())
        restored = Actor.model_validate(data)
        assert restored == actor


class TestReplyTarget:
    def test_creation_minimal(self) -> None:
        rt = ReplyTarget(channel="slack", session_key="sess-1")
        assert rt.channel == "slack"
        assert rt.session_key == "sess-1"
        assert rt.adapter_metadata is None

    def test_creation_with_metadata(self) -> None:
        meta = {"thread_ts": "123.456"}
        rt = ReplyTarget(channel="slack", session_key="sess-1", adapter_metadata=meta)
        assert rt.adapter_metadata == meta

    def test_frozen(self) -> None:
        rt = ReplyTarget(channel="slack", session_key="sess-1")
        with pytest.raises(Exception):  # noqa: B017
            rt.channel = "discord"  # type: ignore[misc]

    def test_json_round_trip(self) -> None:
        rt = ReplyTarget(
            channel="slack",
            session_key="sess-1",
            adapter_metadata={"thread_ts": "123.456"},
        )
        data: dict[str, Any] = json.loads(rt.model_dump_json())
        restored = ReplyTarget.model_validate(data)
        assert restored == rt
