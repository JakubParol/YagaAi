"""Tests for yaga_contracts.handoffs — Handoff dispatch and acceptance DTOs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from yaga_contracts.handoffs import (
    HandoffAcceptance,
    HandoffAck,
    HandoffDispatch,
    HandoffRejection,
)
from yaga_contracts.shared import HandoffStatus

# ── HandoffDispatch ─────────────────────────────────────────────────


class TestHandoffDispatch:
    def _defaults(self, **overrides: Any) -> dict[str, Any]:
        vals: dict[str, Any] = {
            "handoff_id": "ho-1",
            "request_id": "req-1",
            "from_agent": "james",
            "to_agent": "naomi",
            "goal": "Implement feature X",
            "definition_of_done": "All tests pass",
            "callback_target": "james/inbox",
            "correlation_id": "corr-1",
            "causation_id": "cause-1",
            "dedup_key": "dedup-1",
        }
        vals.update(overrides)
        return vals

    def test_creation_all_fields(self) -> None:
        d = HandoffDispatch(**self._defaults())
        assert d.handoff_id == "ho-1"
        assert d.request_id == "req-1"
        assert d.from_agent == "james"
        assert d.to_agent == "naomi"
        assert d.goal == "Implement feature X"
        assert d.definition_of_done == "All tests pass"
        assert d.callback_target == "james/inbox"
        assert d.correlation_id == "corr-1"
        assert d.causation_id == "cause-1"
        assert d.dedup_key == "dedup-1"

    def test_request_id_nullable(self) -> None:
        d = HandoffDispatch(**self._defaults(request_id=None))
        assert d.request_id is None

    def test_causation_id_nullable(self) -> None:
        d = HandoffDispatch(**self._defaults(causation_id=None))
        assert d.causation_id is None

    def test_from_agent_must_differ_from_to_agent(self) -> None:
        with pytest.raises(ValidationError, match=r"from_agent.*to_agent"):
            HandoffDispatch(**self._defaults(from_agent="james", to_agent="james"))

    def test_frozen(self) -> None:
        d = HandoffDispatch(**self._defaults())
        with pytest.raises(Exception):  # noqa: B017
            d.handoff_id = "ho-2"  # type: ignore[misc]


# ── HandoffAck ──────────────────────────────────────────────────────


class TestHandoffAck:
    def test_creation(self) -> None:
        now = datetime.now(tz=UTC)
        ack = HandoffAck(
            handoff_id="ho-1",
            status=HandoffStatus.RECEIVED,
            received_at=now,
        )
        assert ack.handoff_id == "ho-1"
        assert ack.status == HandoffStatus.RECEIVED
        assert ack.received_at == now

    def test_frozen(self) -> None:
        ack = HandoffAck(
            handoff_id="ho-1",
            status=HandoffStatus.RECEIVED,
            received_at=datetime.now(tz=UTC),
        )
        with pytest.raises(Exception):  # noqa: B017
            ack.handoff_id = "ho-2"  # type: ignore[misc]


# ── HandoffAcceptance ───────────────────────────────────────────────


class TestHandoffAcceptance:
    def test_creation(self) -> None:
        now = datetime.now(tz=UTC)
        acc = HandoffAcceptance(
            handoff_id="ho-1",
            status=HandoffStatus.ACCEPTED,
            owner="naomi",
            accepted_at=now,
        )
        assert acc.handoff_id == "ho-1"
        assert acc.status == HandoffStatus.ACCEPTED
        assert acc.owner == "naomi"
        assert acc.accepted_at == now

    def test_frozen(self) -> None:
        acc = HandoffAcceptance(
            handoff_id="ho-1",
            status=HandoffStatus.ACCEPTED,
            owner="naomi",
            accepted_at=datetime.now(tz=UTC),
        )
        with pytest.raises(Exception):  # noqa: B017
            acc.owner = "amos"  # type: ignore[misc]


# ── HandoffRejection ───────────────────────────────────────────────


class TestHandoffRejection:
    def test_creation(self) -> None:
        now = datetime.now(tz=UTC)
        rej = HandoffRejection(
            handoff_id="ho-1",
            status=HandoffStatus.REJECTED,
            assignee="naomi",
            reason="Out of scope",
            rejected_at=now,
        )
        assert rej.handoff_id == "ho-1"
        assert rej.status == HandoffStatus.REJECTED
        assert rej.assignee == "naomi"
        assert rej.reason == "Out of scope"
        assert rej.rejected_at == now

    def test_frozen(self) -> None:
        rej = HandoffRejection(
            handoff_id="ho-1",
            status=HandoffStatus.REJECTED,
            assignee="naomi",
            reason="Out of scope",
            rejected_at=datetime.now(tz=UTC),
        )
        with pytest.raises(Exception):  # noqa: B017
            rej.reason = "Changed mind"  # type: ignore[misc]
