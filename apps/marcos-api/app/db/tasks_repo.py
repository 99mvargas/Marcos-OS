from datetime import datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import class_row
from psycopg.types.json import Json

from app.db.models import Task

# The atomic claim query from docs/RUNTIME_ARCHITECTURE.md §6:
# FOR UPDATE SKIP LOCKED gives exactly-once dispatch under concurrent
# pollers without an application-level mutex.
_CLAIM_NEXT_TASK_SQL = """
    UPDATE tasks
    SET locked_by = %(locked_by)s,
        locked_at = now(),
        lease_expires_at = now() + %(lease)s * interval '1 minute'
    WHERE task_id = (
        SELECT task_id FROM tasks
        WHERE status = 'READY' AND locked_by IS NULL
        ORDER BY priority, created_at
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING *
"""


def claim_next_task(conn: psycopg.Connection, locked_by: str, lease_minutes: int = 45) -> Task | None:
    with conn.cursor(row_factory=class_row(Task)) as cur:
        cur.execute(_CLAIM_NEXT_TASK_SQL, {"locked_by": locked_by, "lease": lease_minutes})
        task = cur.fetchone()
    conn.commit()
    return task


# TASK-0005: generalizes the READY-only claim above to every state that has
# a worker-dispatchable next_agent (docs/RUNTIME_ARCHITECTURE.md §8 — "based
# on next_agent, dispatches..."). Architect/Chairman/Human next_agent values
# are deliberately excluded: those are OpenAI-API or human actions, not a
# headless Claude/Codex worker invocation (TASK-0004's contract), so the
# Orchestrator must never claim them -- they are simply not its job yet.
_DISPATCHABLE_STATUSES = (
    "READY", "RESEARCHING", "ARCHITECTED", "BUILDING", "TESTING",
    "TEST_FAILED", "TROUBLESHOOTING", "REVIEWING", "REVIEW_FAILED",
)
_DISPATCHABLE_ROLES = ("Researcher", "Builder", "Tester", "Reviewer")

_CLAIM_NEXT_DISPATCHABLE_TASK_SQL = """
    UPDATE tasks
    SET locked_by = %(locked_by)s,
        locked_at = now(),
        lease_expires_at = now() + %(lease)s * interval '1 minute'
    WHERE task_id = (
        SELECT task_id FROM tasks
        WHERE status = ANY(%(statuses)s)
          AND next_agent = ANY(%(roles)s)
          AND locked_by IS NULL
          AND human_required = false
        ORDER BY priority, updated_at
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING *
"""


def claim_next_dispatchable_task(
    conn: psycopg.Connection, locked_by: str, lease_minutes: int = 45
) -> Task | None:
    """TASK-0005's Orchestrator claim: any unlocked, non-human-required task
    whose `next_agent` is one of the four roles TASK-0004's worker contract
    actually covers. Same `FOR UPDATE SKIP LOCKED` exactly-once guarantee as
    `claim_next_task` above."""
    with conn.cursor(row_factory=class_row(Task)) as cur:
        cur.execute(
            _CLAIM_NEXT_DISPATCHABLE_TASK_SQL,
            {
                "locked_by": locked_by,
                "lease": lease_minutes,
                "statuses": list(_DISPATCHABLE_STATUSES),
                "roles": list(_DISPATCHABLE_ROLES),
            },
        )
        task = cur.fetchone()
    conn.commit()
    return task


def update_task_status(
    conn: psycopg.Connection,
    task_id: str,
    status: str,
    next_agent: str | None,
    *,
    retry_count: int | None = None,
    files_changed: list[str] | None = None,
    release_lock: bool = True,
) -> None:
    """Deterministic state-machine write: the Orchestrator sets the new
    `status`/`next_agent` a worker's structured result implies, per
    `tasks/README.md` § Lifecycle. Never called to invent a transition the
    lifecycle table doesn't define -- `orchestrator.py` is the single
    caller and owns that mapping."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE tasks
            SET status = %(status)s,
                next_agent = %(next_agent)s,
                retry_count = COALESCE(%(retry_count)s, retry_count),
                files_changed = COALESCE(%(files_changed)s, files_changed),
                locked_by = CASE WHEN %(release_lock)s THEN NULL ELSE locked_by END,
                locked_at = CASE WHEN %(release_lock)s THEN NULL ELSE locked_at END,
                lease_expires_at = CASE WHEN %(release_lock)s THEN NULL ELSE lease_expires_at END
            WHERE task_id = %(task_id)s
            """,
            {
                "task_id": task_id,
                "status": status,
                "next_agent": next_agent,
                "retry_count": retry_count,
                "files_changed": Json(files_changed) if files_changed is not None else None,
                "release_lock": release_lock,
            },
        )
    conn.commit()


def get_task(conn: psycopg.Connection, task_id: str) -> Task | None:
    with conn.cursor(row_factory=class_row(Task)) as cur:
        cur.execute("SELECT * FROM tasks WHERE task_id = %(task_id)s", {"task_id": task_id})
        return cur.fetchone()


def record_event(
    conn: psycopg.Connection, task_id: str, actor: str, event_type: str, detail: dict[str, Any] | None = None
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO task_events (task_id, actor, event_type, detail)
            VALUES (%(task_id)s, %(actor)s, %(event_type)s, %(detail)s)
            """,
            {"task_id": task_id, "actor": actor, "event_type": event_type, "detail": psycopg.types.json.Json(detail or {})},
        )
    conn.commit()


def release_expired_leases(conn: psycopg.Connection) -> list[str]:
    """Lease-expiry sweep (docs/RUNTIME_ARCHITECTURE.md §8, §15): un-claim
    any task whose lease has expired, so it becomes eligible for retry or
    escalation. Returns the released task_ids."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE tasks
            SET locked_by = NULL, locked_at = NULL, lease_expires_at = NULL
            WHERE locked_by IS NOT NULL AND lease_expires_at < %(now)s
            RETURNING task_id
            """,
            {"now": datetime.now(timezone.utc)},
        )
        released = [row[0] for row in cur.fetchall()]
    conn.commit()
    return released
