"""HTTP request/response DTOs for the Yaga API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from yaga_contracts.shared import PublishStatus, ReplyTarget, RequestStatus

# ── Request DTOs ─────────────────────────────────────────────────────


class RequestPayload(BaseModel):
    """Free-text payload submitted with an inbound request."""

    model_config = ConfigDict(frozen=True)

    text: str


class CreateRequestBody(BaseModel):
    """Body sent by an adapter to create a new inbound request."""

    model_config = ConfigDict(frozen=True)

    origin: str
    payload: RequestPayload
    reply_target: ReplyTarget


# ── Response DTOs ────────────────────────────────────────────────────


class CreateRequestResponse(BaseModel):
    """Acknowledgement returned after a request is accepted."""

    model_config = ConfigDict(frozen=True)

    status: Literal["accepted"]
    request_id: str
    task_ref: str | None


# ── Read Models ──────────────────────────────────────────────────────


class RequestReadModel(BaseModel):
    """Full read-side projection of a request."""

    model_config = ConfigDict(frozen=True)

    request_id: str
    correlation_id: str
    status: RequestStatus
    reply_publish_status: PublishStatus
    origin: str
    strategic_owner_agent_id: str | None
    reply_target: ReplyTarget | None
    created_at: datetime
    updated_at: datetime


# ── Error DTOs ───────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    """Structured error information."""

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    details: list[Any] = []


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all API endpoints."""

    model_config = ConfigDict(frozen=True)

    error: ErrorDetail
