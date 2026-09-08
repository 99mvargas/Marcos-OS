from datetime import datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import class_row

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
