"""Tests for yaga_contracts.shared — enums and value objects."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest
from pydantic import ValidationError

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
        "Created",
        "Accepted",
        "In Progress",
        "Review",
        "Verify",
        "Done",
        "Blocked",
        "Escalated",
        "Cancelled",
    ]

    def test_members(self) -> None:
        assert [m.value for m in TaskStatus] == self.expected

    def test_str_identity(self) -> None:
        assert TaskStatus.CREATED == "Created"


class TestHandoffStatus:
    expected = ["received", "accepted", "rejected"]

    def test_members(self) -> None:
        assert [m.value for m in HandoffStatus] == self.expected

    def test_str_identity(self) -> None:
        assert HandoffStatus.RECEIVED == "received"


class TestRequestStatus:
    expected = [
        "received",
        "normalized",
        "delegated",
        "awaiting_callback",
        "reply_pending",
        "reply_published",
        "reply_failed",
        "fallback_required",
        "closed",
    ]

    def test_members(self) -> None:
        assert [m.value for m in RequestStatus] == self.expected

    def test_str_identity(self) -> None:
        assert RequestStatus.CLOSED == "closed"


class TestPublishStatus:
    expected = [
        "pending",
        "attempted",
        "published",
        "failed",
        "unknown",
        "fallback_required",
        "abandoned",
    ]

    def test_members(self) -> None:
        assert [m.value for m in PublishStatus] == self.expected

    def test_str_identity(self) -> None:
        assert PublishStatus.PENDING == "pending"


class TestRequestClass:
    expected = ["session_bound", "durable"]

    def test_members(self) -> None:
        assert [m.value for m in RequestClass] == self.expected

    def test_str_identity(self) -> None:
        assert RequestClass.DURABLE == "durable"


class TestExecutionMode:
    expected = ["session_bound", "detached"]

    def test_members(self) -> None:
        assert [m.value for m in ExecutionMode] == self.expected

    def test_str_identity(self) -> None:
        assert ExecutionMode.DETACHED == "detached"


class TestHandoffResolution:
    expected = ["accepted", "rejected"]

    def test_members(self) -> None:
        assert [m.value for m in HandoffResolution] == self.expected

    def test_str_identity(self) -> None:
        assert HandoffResolution.ACCEPTED == "accepted"


class TestTaskOutcome:
    expected = ["done", "failed", "blocked"]

    def test_members(self) -> None:
        assert [m.value for m in TaskOutcome] == self.expected

    def test_str_identity(self) -> None:
        assert TaskOutcome.DONE == "done"


class TestJobStatus:
    expected = ["scheduled", "running", "completed", "failed", "cancelled"]

    def test_members(self) -> None:
        assert [m.value for m in JobStatus] == self.expected

    def test_str_identity(self) -> None:
        assert JobStatus.SCHEDULED == "scheduled"


class TestCommandStatus:
    expected = ["accepted", "rejected", "processed"]

    def test_members(self) -> None:
        assert [m.value for m in CommandStatus] == self.expected

    def test_str_identity(self) -> None:
        assert CommandStatus.PROCESSED == "processed"


class TestOutboxStatus:
    expected = ["pending", "dispatched", "failed"]

    def test_members(self) -> None:
        assert [m.value for m in OutboxStatus] == self.expected

    def test_str_identity(self) -> None:
        assert OutboxStatus.DISPATCHED == "dispatched"


# ── Value object tests ────────────────────────────────────────────────


class TestActor:
    def test_creation(self) -> None:
        actor = Actor(type="agent", id="james-001")
        assert actor.type == "agent"
        assert actor.id == "james-001"

    def test_frozen(self) -> None:
        actor = Actor(type="runtime", id="rt-1")
        with pytest.raises(ValidationError):
            cast(Any, actor).type = "adapter"

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
        with pytest.raises(ValidationError):
            cast(Any, rt).channel = "discord"

    def test_json_round_trip(self) -> None:
        rt = ReplyTarget(
            channel="slack",
            session_key="sess-1",
            adapter_metadata={"thread_ts": "123.456"},
        )
        data: dict[str, Any] = json.loads(rt.model_dump_json())
        restored = ReplyTarget.model_validate(data)
        assert restored == rt
