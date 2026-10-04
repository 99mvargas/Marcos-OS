"""Structured result contract every headless worker invocation returns.

Per docs/AUTONOMOUS_AGENT_PROTOCOL.md's "agents communicate through
structured artifacts, not prose" requirement: TASK-0005's Orchestrator and
Verifier read these typed fields to decide the next task state. They never
parse a free-text transcript -- the full transcript is saved to disk
(`raw_output_path`) for audit/debugging, not inlined here, per
docs/TOKEN_EFFICIENCY.md's context-minimization rules.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

WorkerStatus = Literal["success", "failure", "needs_human", "timeout"]
Provider = Literal["claude-code", "codex"]


class HumanRequiredBlock(BaseModel):
    """Mirrors the schema in docs/AUTONOMOUS_AGENT_PROTOCOL.md §8."""

    reason: str
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    action_required: str
    safe_to_pause: bool
    resume_condition: str


class WorkerResult(BaseModel):
    task_id: str
    role: str
    provider: Provider
    model: str | None
    status: WorkerStatus
    summary: str
    files_changed: list[str] = []
    tests: list[dict[str, Any]] = []
    human_required: HumanRequiredBlock | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    duration_ms: int
    exit_code: int
    permission_denials: list[Any] = []
    error: str | None = None
    raw_output_path: str
