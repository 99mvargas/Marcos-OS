"""Deterministic Python Orchestrator (TASK-0005).

Implements the Orchestrator role (docs/AGENT_ROLES.md §7) as plain code
polling Postgres directly -- per DEC-010, which supersedes DEC-007's
"n8n is the Orchestrator" design. One call to `run_cycle()` is one
claim-dispatch-apply pass; a scheduler (cron, systemd timer, or a simple
sleep loop) calls it repeatedly. The orchestrator itself contains no
scheduling framework -- that would be the "Kubernetes for a single-operator
system" overbuild §23 of docs/RUNTIME_ARCHITECTURE.md already rejected for
a different component, same reasoning applies here.

Scope deliberately stops at `CHECKPOINT`: once a Reviewer pass succeeds,
this orchestrator does **not** auto-dispatch a headless Builder invocation
to perform the 9-step checkpoint procedure (commit/push against a real
repo, unattended). That is `HUMAN_REQUIRED_QUEUE.md` #2's concern applied
structurally -- `CHECKPOINT` is intentionally absent from the dispatchable
status set in `tasks_repo.py`. A human-directed Claude Code session (what
every checkpoint in this repository's own history has been) performs the
actual checkpoint; this orchestrator gets everything up to that point
ready for one.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

import psycopg

from app.db import tasks_repo
from app.db.human_queue_repo import raise_human_required
from app.db.invocations_repo import complete_invocation, start_invocation
from app.runtime import verifier
from app.runtime.claude_worker import invoke_claude
from app.runtime.codex_worker import invoke_codex
from app.runtime.worker_result import WorkerResult

MAX_RETRY_COUNT = 3
WORKTREE_ROOT = "/home/mvargas99/workspace/marcos-os-worktrees"

# WorkerResult.status (TASK-0004's vocabulary: success/failure/timeout/
# needs_human) is not the same enum as agent_invocations.status (TASK-0003's
# schema: queued/running/succeeded/failed/timed_out) -- this is the mapping
# between them, not a shared vocabulary.
_WORKER_STATUS_TO_INVOCATION_STATUS: dict[str, str] = {
    "success": "succeeded",
    "failure": "failed",
    "timeout": "timed_out",
    "needs_human": "failed",
}

# (status, role) -> status to move to *before* dispatch, so the task is
# visibly "in progress" under the right label while the invocation runs.
# Anything not listed here dispatches without changing status first (e.g.
# resuming in the same status after a lease release).
_PRE_DISPATCH_NORMALIZE: dict[tuple[str, str], str] = {
    ("READY", "Researcher"): "RESEARCHING",
    ("ARCHITECTED", "Builder"): "BUILDING",
    ("TEST_FAILED", "Builder"): "TROUBLESHOOTING",
    ("REVIEW_FAILED", "Builder"): "BUILDING",
}

_POST_SUCCESS: dict[str, tuple[str, str]] = {
    "Researcher": ("ARCHITECTED", "Architect"),
    "Builder": ("TESTING", "Tester"),
    "Tester": ("REVIEWING", "Reviewer"),
    "Reviewer": ("CHECKPOINT", "Builder"),
}

_POST_FAILURE: dict[str, tuple[str, str]] = {
    "Researcher": ("BLOCKED", "Architect"),
    "Tester": ("TEST_FAILED", "Builder"),
    "Reviewer": ("REVIEW_FAILED", "Builder"),
    # Builder on failure: no entry -- handled specially in apply_result
    # (self-retry in place up to MAX_RETRY_COUNT; the Watchdog escalates
    # past that, not the Orchestrator).
}


@dataclass
class CycleResult:
    task_id: str | None
    role: str | None
    dispatched: bool
    worker_result: WorkerResult | None = None
    note: str = ""


def _build_role_prompt(task: tasks_repo.Task, role: str) -> str:
    """Targeted context selection (docs/TOKEN_EFFICIENCY.md): the task
    row's own fields are the pointer list, not a repository dump."""
    lines = [
        f"You are acting as the {role} role on {task.task_id}.",
        f"Objective: {task.objective.strip()}",
        "Requirements:",
        *(f"  - {r}" for r in task.requirements),
    ]
    if task.architecture_reference:
        lines.append("Architecture reference (read these, do not re-derive from scratch):")
        lines += [f"  - {r}" for r in task.architecture_reference]
    if task.files_changed:
        lines.append("Files already touched by prior roles on this task:")
        lines += [f"  - {f}" for f in task.files_changed]
    if role == "Tester":
        lines.append("Verify actual behavior (real commands/tests), not just that files look right.")
    if role == "Reviewer":
        lines.append(
            "Actively look for problems per docs/AUTONOMOUS_AGENT_PROTOCOL.md §11 "
            "-- do not rubber-stamp."
        )
    return "\n".join(lines)


def _dispatch(
    task: tasks_repo.Task, role: str, provider: str, model: str, cwd: str
) -> WorkerResult:
    prompt = _build_role_prompt(task, role)
    if provider == "codex":
        return invoke_codex(task_id=task.task_id, role=role, prompt=prompt, cwd=cwd, model=model or None)
    return invoke_claude(task_id=task.task_id, role=role, prompt=prompt, cwd=cwd, model=model)


def run_cycle(
    conn: psycopg.Connection,
    *,
    locked_by: str,
    provider: str = "claude-code",
    model: str = "claude-haiku-4-5",
    worktree_root: str = WORKTREE_ROOT,
    run_verifier: bool = True,
) -> CycleResult:
    """One claim-dispatch-apply pass. Sweeps expired leases first so a
    crashed prior invocation's task is eligible again before claiming."""
    tasks_repo.release_expired_leases(conn)

    task = tasks_repo.claim_next_dispatchable_task(conn, locked_by=locked_by)
    if task is None:
        return CycleResult(task_id=None, role=None, dispatched=False, note="no claimable task")

    role = task.next_agent
    assert role is not None  # claim query already filtered on next_agent being set

    cwd = f"{worktree_root}/{task.task_id}"
    import os

    if not os.path.isdir(cwd):
        raise_human_required(
            conn,
            task_id=task.task_id,
            reason="WORKTREE_MISSING",
            risk="LOW",
            action_required=(
                f"No worktree found at {cwd} for {task.task_id}. The Orchestrator "
                "does not provision worktrees itself (deliberate v0.1 scope limit) "
                "-- create one (`git worktree add`) before this task can be dispatched."
            ),
            resume_condition=f"{cwd} exists as a valid worktree of this repository.",
        )
        tasks_repo.update_task_status(
            conn, task.task_id, status=task.status, next_agent=role, release_lock=True
        )
        return CycleResult(task_id=task.task_id, role=role, dispatched=False, note="worktree missing")

    pre_status = _PRE_DISPATCH_NORMALIZE.get((task.status, role), task.status)
    if pre_status != task.status:
        tasks_repo.record_event(
            conn, task.task_id, actor="Orchestrator", event_type="status_transition",
            detail={"from": task.status, "to": pre_status, "reason": "pre_dispatch_normalize"},
        )

    invocation_id = uuid.uuid4()
    start_invocation(conn, invocation_id, task.task_id, role=role, provider=provider, model=model)
    tasks_repo.record_event(
        conn, task.task_id, actor="Orchestrator", event_type="invocation_dispatched",
        detail={"invocation_id": str(invocation_id), "role": role, "provider": provider},
    )

    result = _dispatch(task, role, provider, model, cwd)

    complete_invocation(
        conn, invocation_id, status=_WORKER_STATUS_TO_INVOCATION_STATUS[result.status],
        input_tokens=result.input_tokens, output_tokens=result.output_tokens,
        duration_ms=result.duration_ms, result=result.model_dump(mode="json"), error=result.error,
    )

    verification = None
    if run_verifier and role in ("Builder", "Tester") and result.status == "success":
        verification = verifier.verify(cwd=cwd, files_changed=result.files_changed)
        if not verification.passed:
            result = result.model_copy(update={"status": "failure"})
            tasks_repo.record_event(
                conn, task.task_id, actor="Verifier", event_type="verification_failed",
                detail={"checks": verification.checks},
            )

    apply_result(conn, task, role, pre_status, result)
    return CycleResult(task_id=task.task_id, role=role, dispatched=True, worker_result=result)


def apply_result(
    conn: psycopg.Connection, task: tasks_repo.Task, role: str, pre_status: str, result: WorkerResult
) -> None:
    """The deterministic state-machine write -- no LLM call decides the
    next status, the lifecycle table does (tasks/README.md § Lifecycle)."""
    if result.status == "needs_human" or result.human_required:
        action = result.human_required
        raise_human_required(
            conn,
            task_id=task.task_id,
            reason=action.reason if action else "WORKER_REQUESTED_HUMAN",
            risk=action.risk if action else "MEDIUM",
            action_required=action.action_required if action else result.summary,
            resume_condition=action.resume_condition if action else "Manually reviewed and resumed.",
            safe_to_pause=action.safe_to_pause if action else True,
        )
        tasks_repo.update_task_status(conn, task.task_id, status=pre_status, next_agent=role, release_lock=True)
        return

    if result.status == "success":
        new_status, new_next_agent = _POST_SUCCESS[role]
        tasks_repo.update_task_status(
            conn, task.task_id, status=new_status, next_agent=new_next_agent,
            files_changed=(task.files_changed + result.files_changed) or None,
        )
        tasks_repo.record_event(
            conn, task.task_id, actor="Orchestrator", event_type="status_transition",
            detail={"from": pre_status, "to": new_status, "role": role, "outcome": "success"},
        )
        return

    # failure / timeout
    if role == "Builder":
        retry_count = task.retry_count + 1
        if retry_count >= MAX_RETRY_COUNT:
            # Leave claimed=false but do not re-queue indefinitely -- the
            # Watchdog (watchdog.py) is the one that escalates a task whose
            # retry_count has hit the cap to HUMAN_REQUIRED, not the
            # Orchestrator itself (single-responsibility: this function
            # only ever records what happened on *this* attempt).
            tasks_repo.update_task_status(
                conn, task.task_id, status=pre_status, next_agent=role, retry_count=retry_count
            )
        else:
            tasks_repo.update_task_status(
                conn, task.task_id, status=pre_status, next_agent=role, retry_count=retry_count
            )
        tasks_repo.record_event(
            conn, task.task_id, actor="Orchestrator", event_type="invocation_failed",
            detail={"role": role, "retry_count": retry_count, "error": result.error, "summary": result.summary[:500]},
        )
        return

    new_status, new_next_agent = _POST_FAILURE[role]
    tasks_repo.update_task_status(conn, task.task_id, status=new_status, next_agent=new_next_agent)
    tasks_repo.record_event(
        conn, task.task_id, actor="Orchestrator", event_type="status_transition",
        detail={"from": pre_status, "to": new_status, "role": role, "outcome": "failure"},
    )
