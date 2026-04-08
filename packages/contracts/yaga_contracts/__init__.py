"""Shared schemas for HTTP, A2A, events, and commands."""

from .commands import (
    AcceptHandoffCommand,
    AcceptRequestCommand,
    CancelJobCommand,
    CommandBase,
    CompleteTaskCommand,
    CreateTaskCommand,
    DispatchHandoffCommand,
    RecordPublicationAttemptCommand,
    RecordPublicationResultCommand,
    RejectHandoffCommand,
    ScheduleJobCommand,
)
from .events import (
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
from .handoffs import (
    HandoffAcceptance,
    HandoffAck,
    HandoffDispatch,
    HandoffRejection,
)
from .http import (
    CreateRequestBody,
    CreateRequestResponse,
    ErrorDetail,
    ErrorResponse,
    RequestPayload,
    RequestReadModel,
)
from .shared import (
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
from .webhooks import (
    WEBHOOK_EVENT_ID_HEADER,
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_TIMESTAMP_HEADER,
    WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS,
    PublicationStatusWebhook,
)

__all__ = [
    # shared.py
    "TaskStatus",
    "HandoffStatus",
    "RequestStatus",
    "PublishStatus",
    "RequestClass",
    "ExecutionMode",
    "HandoffResolution",
    "TaskOutcome",
    "JobStatus",
    "CommandStatus",
    "OutboxStatus",
    "Actor",
    "ReplyTarget",
    # http.py
    "RequestPayload",
    "CreateRequestBody",
    "CreateRequestResponse",
    "RequestReadModel",
    "ErrorDetail",
    "ErrorResponse",
    # events.py
    "EventEnvelope",
    "RequestReceivedPayload",
    "RequestNormalizationPayload",
    "TaskLifecyclePayload",
    "HandoffLifecyclePayload",
    "CallbackPayload",
    "PublicationPayload",
    "WatchdogPayload",
    "CommandRejectedPayload",
    # handoffs.py
    "HandoffDispatch",
    "HandoffAck",
    "HandoffAcceptance",
    "HandoffRejection",
    # webhooks.py
    "PublicationStatusWebhook",
    "WEBHOOK_SIGNATURE_HEADER",
    "WEBHOOK_TIMESTAMP_HEADER",
    "WEBHOOK_EVENT_ID_HEADER",
    "WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS",
    # commands.py
    "CommandBase",
    "AcceptRequestCommand",
    "CreateTaskCommand",
    "DispatchHandoffCommand",
    "AcceptHandoffCommand",
    "RejectHandoffCommand",
    "CompleteTaskCommand",
    "RecordPublicationAttemptCommand",
    "RecordPublicationResultCommand",
    "ScheduleJobCommand",
    "CancelJobCommand",
]
