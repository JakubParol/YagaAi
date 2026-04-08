"""Tests for yaga_contracts.commands — command base and dispatch commands."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from yaga_contracts.commands import (
    AcceptHandoffCommand,
    AcceptRequestCommand,
    CommandBase,
    CreateTaskCommand,
    DispatchHandoffCommand,
    RejectHandoffCommand,
)
from yaga_contracts.http import RequestPayload
from yaga_contracts.shared import (
    Actor,
    ExecutionMode,
    ReplyTarget,
    RequestClass,
)

# ── Helpers ──────────────────────────────────────────────────────────

_NOW = datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC)
_ACTOR = Actor(type="agent", id="james-001")


def _base_kwargs(**overrides: Any) -> dict[str, Any]:
    """Return a complete set of kwargs for CommandBase fields."""
    base: dict[str, Any] = {
        "command_id": "cmd-1",
        "command_type": "accept_request",
        "aggregate_type": "request",
        "aggregate_id": "req-1",
        "correlation_id": "corr-1",
        "dedup_key": "dedup-1",
        "occurred_at": _NOW,
        "actor": _ACTOR,
    }
    base.update(overrides)
    return base


# ── CommandBase ──────────────────────────────────────────────────────


class TestCommandBase:
    def test_creation_all_fields(self) -> None:
        cmd = CommandBase(**_base_kwargs(causation_id="cause-1"))
        assert cmd.command_id == "cmd-1"
        assert cmd.command_type == "accept_request"
        assert cmd.aggregate_type == "request"
        assert cmd.aggregate_id == "req-1"
        assert cmd.correlation_id == "corr-1"
        assert cmd.causation_id == "cause-1"
        assert cmd.dedup_key == "dedup-1"
        assert cmd.occurred_at == _NOW
        assert cmd.actor == _ACTOR

    def test_causation_id_optional(self) -> None:
        cmd = CommandBase(**_base_kwargs())
        assert cmd.causation_id is None

    def test_schema_version_defaults_to_v1(self) -> None:
        cmd = CommandBase(**_base_kwargs())
        assert cmd.schema_version == "v1"

    def test_frozen(self) -> None:
        cmd = CommandBase(**_base_kwargs())
        with pytest.raises(ValidationError):
            cmd.command_id = "changed"  # type: ignore[misc]


# ── AcceptRequestCommand ─────────────────────────────────────────────


class TestAcceptRequestCommand:
    def test_creation(self) -> None:
        cmd = AcceptRequestCommand(
            **_base_kwargs(command_type="accept_request"),
            request_id="req-1",
            idempotency_key="idem-1",
            origin="slack",
            request_class=RequestClass.SESSION_BOUND,
            payload=RequestPayload(text="Hello"),
        )
        assert cmd.command_type == "accept_request"
        assert cmd.request_id == "req-1"
        assert cmd.idempotency_key == "idem-1"
        assert cmd.origin == "slack"
        assert cmd.origin_session_key is None
        assert cmd.request_class == RequestClass.SESSION_BOUND
        assert cmd.reply_target is None
        assert cmd.payload == RequestPayload(text="Hello")

    def test_full_with_optional_fields(self) -> None:
        rt = ReplyTarget(channel="slack", session_key="sess-1")
        cmd = AcceptRequestCommand(
            **_base_kwargs(command_type="accept_request"),
            request_id="req-1",
            idempotency_key="idem-1",
            origin="slack",
            origin_session_key="sess-1",
            request_class=RequestClass.DURABLE,
            reply_target=rt,
            payload=RequestPayload(text="Hello"),
        )
        assert cmd.origin_session_key == "sess-1"
        assert cmd.reply_target == rt

    def test_command_type_literal(self) -> None:
        with pytest.raises(ValidationError):
            AcceptRequestCommand(
                **_base_kwargs(command_type="wrong_type"),
                request_id="req-1",
                idempotency_key="idem-1",
                origin="slack",
                request_class=RequestClass.SESSION_BOUND,
                payload=RequestPayload(text="Hello"),
            )


# ── CreateTaskCommand ────────────────────────────────────────────────


class TestCreateTaskCommand:
    def test_creation(self) -> None:
        cmd = CreateTaskCommand(
            **_base_kwargs(command_type="create_task"),
            task_id="task-1",
            request_id="req-1",
            owner_agent="james-001",
            callback_target="cb-1",
        )
        assert cmd.command_type == "create_task"
        assert cmd.task_id == "task-1"
        assert cmd.request_id == "req-1"
        assert cmd.owner_agent == "james-001"
        assert cmd.callback_target == "cb-1"

    def test_command_type_literal(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskCommand(
                **_base_kwargs(command_type="wrong_type"),
                task_id="task-1",
                request_id="req-1",
                owner_agent="james-001",
                callback_target="cb-1",
            )


# ── DispatchHandoffCommand ───────────────────────────────────────────


class TestDispatchHandoffCommand:
    def test_creation(self) -> None:
        cmd = DispatchHandoffCommand(
            **_base_kwargs(command_type="dispatch_handoff"),
            handoff_id="ho-1",
            task_id="task-1",
            from_agent="james-001",
            to_agent="naomi-001",
            goal="Implement feature X",
            definition_of_done="Tests pass",
            callback_target="cb-1",
            execution_mode=ExecutionMode.DETACHED,
        )
        assert cmd.command_type == "dispatch_handoff"
        assert cmd.handoff_id == "ho-1"
        assert cmd.task_id == "task-1"
        assert cmd.request_id is None
        assert cmd.from_agent == "james-001"
        assert cmd.to_agent == "naomi-001"
        assert cmd.goal == "Implement feature X"
        assert cmd.definition_of_done == "Tests pass"
        assert cmd.callback_target == "cb-1"
        assert cmd.execution_mode == ExecutionMode.DETACHED

    def test_with_request_id(self) -> None:
        cmd = DispatchHandoffCommand(
            **_base_kwargs(command_type="dispatch_handoff"),
            handoff_id="ho-1",
            task_id="task-1",
            request_id="req-1",
            from_agent="james-001",
            to_agent="naomi-001",
            goal="Implement feature X",
            definition_of_done="Tests pass",
            callback_target="cb-1",
            execution_mode=ExecutionMode.SESSION_BOUND,
        )
        assert cmd.request_id == "req-1"

    def test_command_type_literal(self) -> None:
        with pytest.raises(ValidationError):
            DispatchHandoffCommand(
                **_base_kwargs(command_type="wrong_type"),
                handoff_id="ho-1",
                task_id="task-1",
                from_agent="james-001",
                to_agent="naomi-001",
                goal="Implement feature X",
                definition_of_done="Tests pass",
                callback_target="cb-1",
                execution_mode=ExecutionMode.DETACHED,
            )


# ── AcceptHandoffCommand ────────────────────────────────────────────


class TestAcceptHandoffCommand:
    def test_creation(self) -> None:
        cmd = AcceptHandoffCommand(
            **_base_kwargs(command_type="accept_handoff"),
            handoff_id="ho-1",
            task_id="task-1",
            responder_agent="naomi-001",
        )
        assert cmd.command_type == "accept_handoff"
        assert cmd.handoff_id == "ho-1"
        assert cmd.task_id == "task-1"
        assert cmd.responder_agent == "naomi-001"

    def test_command_type_literal(self) -> None:
        with pytest.raises(ValidationError):
            AcceptHandoffCommand(
                **_base_kwargs(command_type="wrong_type"),
                handoff_id="ho-1",
                task_id="task-1",
                responder_agent="naomi-001",
            )


# ── RejectHandoffCommand ────────────────────────────────────────────


class TestRejectHandoffCommand:
    def test_creation(self) -> None:
        cmd = RejectHandoffCommand(
            **_base_kwargs(command_type="reject_handoff"),
            handoff_id="ho-1",
            task_id="task-1",
            responder_agent="naomi-001",
            reason="Not my area",
        )
        assert cmd.command_type == "reject_handoff"
        assert cmd.handoff_id == "ho-1"
        assert cmd.reason == "Not my area"

    def test_command_type_literal(self) -> None:
        with pytest.raises(ValidationError):
            RejectHandoffCommand(
                **_base_kwargs(command_type="wrong_type"),
                handoff_id="ho-1",
                task_id="task-1",
                responder_agent="naomi-001",
                reason="Not my area",
            )
