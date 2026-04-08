"""Handoff dispatch and acceptance DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

# ── Dispatch ────────────────────────────────────────────────────────


class HandoffDispatch(BaseModel):
    """Instruction from one agent to hand work off to another."""

    model_config = ConfigDict(frozen=True)

    handoff_id: str
    request_id: str | None = None
    from_agent: str
    to_agent: str
    goal: str
    definition_of_done: str
    callback_target: str
    correlation_id: str
    causation_id: str | None = None
    dedup_key: str

    @model_validator(mode="after")
    def _agents_must_differ(self) -> HandoffDispatch:
        if self.from_agent == self.to_agent:
            msg = "from_agent and to_agent must differ"
            raise ValueError(msg)
        return self


# ── Acknowledgement / Acceptance / Rejection ────────────────────────


class HandoffAck(BaseModel):
    """Immediate acknowledgement that a handoff was received."""

    model_config = ConfigDict(frozen=True)

    handoff_id: str
    status: Literal["received"] = "received"
    received_at: datetime


class HandoffAcceptance(BaseModel):
    """Confirmation that the target agent accepted the handoff."""

    model_config = ConfigDict(frozen=True)

    handoff_id: str
    status: Literal["accepted"] = "accepted"
    owner: str
    accepted_at: datetime


class HandoffRejection(BaseModel):
    """Notification that the target agent rejected the handoff."""

    model_config = ConfigDict(frozen=True)

    handoff_id: str
    status: Literal["rejected"] = "rejected"
    assignee: str
    reason: str
    rejected_at: datetime
