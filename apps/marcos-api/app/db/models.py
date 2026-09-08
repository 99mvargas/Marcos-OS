from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    objective: str
    status: str
    assigned_agent: str
    next_agent: str | None
    priority: str
    requirements: list[Any]
    architecture_reference: list[Any]
    files_changed: list[Any]
    tests: list[Any]
    blockers: list[Any]
    decisions: list[Any]
    human_required: bool
    human_action: dict[str, Any] | None
    locked_by: str | None
    locked_at: datetime | None
    lease_expires_at: datetime | None
    retry_count: int
    created_at: datetime
    updated_at: datetime


class TaskEvent(BaseModel):
    id: int
    task_id: str
    at: datetime
    actor: str
    event_type: str
    detail: dict[str, Any]


class AgentInvocation(BaseModel):
    invocation_id: UUID
    task_id: str
    role: str
    provider: str
    model: str | None
    status: str
    retry_count: int
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: Decimal | None
    duration_ms: int | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    result: dict[str, Any] | None
    error: str | None


class HumanRequiredEntry(BaseModel):
    id: int
    task_id: str
    reason: str
    risk: str
    action_required: str
    safe_to_pause: bool
    resume_condition: str
    raised_at: datetime
    notified_at: datetime | None
    resolved_at: datetime | None


class Checkpoint(BaseModel):
    id: int
    task_id: str
    branch: str
    commit_sha: str
    pushed: bool
    written_at: datetime
