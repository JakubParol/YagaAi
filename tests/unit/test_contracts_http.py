"""Tests for yaga_contracts.http — HTTP request/response DTOs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from yaga_contracts.http import (
    CreateRequestBody,
    CreateRequestResponse,
    ErrorDetail,
    ErrorResponse,
    RequestPayload,
    RequestReadModel,
)
from yaga_contracts.shared import PublishStatus, ReplyTarget, RequestStatus

# ── RequestPayload ───────────────────────────────────────────────────


class TestRequestPayload:
    def test_creation(self) -> None:
        p = RequestPayload(text="hello")
        assert p.text == "hello"

    def test_text_required(self) -> None:
        with pytest.raises(ValidationError):
            RequestPayload()  # type: ignore[call-arg]

    def test_frozen(self) -> None:
        p = RequestPayload(text="hello")
        with pytest.raises(ValidationError):
            p.text = "bye"  # type: ignore[misc]


# ── CreateRequestBody ────────────────────────────────────────────────


class TestCreateRequestBody:
    def _reply_target(self) -> ReplyTarget:
        return ReplyTarget(channel="slack", session_key="sess-1")

    def test_creation(self) -> None:
        body = CreateRequestBody(
            origin="slack-adapter",
            payload=RequestPayload(text="do something"),
            reply_target=self._reply_target(),
        )
        assert body.origin == "slack-adapter"
        assert body.payload.text == "do something"
        assert body.reply_target.channel == "slack"

    def test_reply_target_required(self) -> None:
        with pytest.raises(ValidationError):
            CreateRequestBody(
                origin="slack-adapter",
                payload=RequestPayload(text="hi"),
            )  # type: ignore[call-arg]

    def test_frozen(self) -> None:
        body = CreateRequestBody(
            origin="slack-adapter",
            payload=RequestPayload(text="hi"),
            reply_target=self._reply_target(),
        )
        with pytest.raises(ValidationError):
            body.origin = "other"  # type: ignore[misc]


# ── CreateRequestResponse ────────────────────────────────────────────


class TestCreateRequestResponse:
    def test_creation(self) -> None:
        resp = CreateRequestResponse(
            status="accepted",
            request_id="req-1",
            task_ref="task-1",
        )
        assert resp.status == "accepted"
        assert resp.request_id == "req-1"
        assert resp.task_ref == "task-1"

    def test_literal_rejects_other_values(self) -> None:
        with pytest.raises(ValidationError):
            CreateRequestResponse(
                status="rejected",  # type: ignore[arg-type]
                request_id="req-1",
                task_ref=None,
            )

    def test_task_ref_nullable(self) -> None:
        resp = CreateRequestResponse(
            status="accepted",
            request_id="req-1",
            task_ref=None,
        )
        assert resp.task_ref is None

    def test_frozen(self) -> None:
        resp = CreateRequestResponse(
            status="accepted", request_id="req-1", task_ref=None
        )
        with pytest.raises(ValidationError):
            resp.status = "accepted"  # type: ignore[misc]


# ── RequestReadModel ─────────────────────────────────────────────────


class TestRequestReadModel:
    def _make(self, **overrides: Any) -> RequestReadModel:
        now = datetime.now(tz=UTC)
        defaults: dict[str, Any] = {
            "request_id": "req-1",
            "correlation_id": "corr-1",
            "status": RequestStatus.RECEIVED,
            "reply_publish_status": PublishStatus.PENDING,
            "origin": "slack-adapter",
            "strategic_owner_agent_id": None,
            "reply_target": None,
            "created_at": now,
            "updated_at": now,
        }
        defaults.update(overrides)
        return RequestReadModel(**defaults)

    def test_creation(self) -> None:
        m = self._make()
        assert m.request_id == "req-1"
        assert m.status == RequestStatus.RECEIVED

    def test_json_round_trip(self) -> None:
        rt = ReplyTarget(channel="slack", session_key="sess-1")
        m = self._make(
            reply_target=rt,
            strategic_owner_agent_id="james-001",
        )
        data: dict[str, Any] = json.loads(m.model_dump_json())
        restored = RequestReadModel.model_validate(data)
        assert restored == m

    def test_frozen(self) -> None:
        m = self._make()
        with pytest.raises(ValidationError):
            m.status = RequestStatus.CLOSED  # type: ignore[misc]


# ── ErrorDetail / ErrorResponse ──────────────────────────────────────


class TestErrorDetail:
    def test_creation(self) -> None:
        d = ErrorDetail(code="NOT_FOUND", message="Request not found")
        assert d.code == "NOT_FOUND"
        assert d.message == "Request not found"
        assert d.details == []

    def test_details_default_empty(self) -> None:
        d = ErrorDetail(code="X", message="Y")
        assert d.details == []

    def test_frozen(self) -> None:
        d = ErrorDetail(code="X", message="Y")
        with pytest.raises(ValidationError):
            d.code = "Z"  # type: ignore[misc]


class TestErrorResponse:
    def test_creation(self) -> None:
        resp = ErrorResponse(
            error=ErrorDetail(code="BAD_REQUEST", message="Invalid input")
        )
        assert resp.error.code == "BAD_REQUEST"

    def test_wire_format(self) -> None:
        resp = ErrorResponse(
            error=ErrorDetail(
                code="NOT_FOUND",
                message="Request not found",
                details=["extra-info"],
            )
        )
        data: dict[str, Any] = json.loads(resp.model_dump_json())
        assert data == {
            "error": {
                "code": "NOT_FOUND",
                "message": "Request not found",
                "details": ["extra-info"],
            }
        }

    def test_frozen(self) -> None:
        resp = ErrorResponse(error=ErrorDetail(code="X", message="Y"))
        with pytest.raises(ValidationError):
            resp.error = ErrorDetail(code="A", message="B")  # type: ignore[misc]
