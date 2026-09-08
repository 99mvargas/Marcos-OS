from typing import Any

import psycopg
from psycopg.types.json import Json


def raise_human_required(
    conn: psycopg.Connection,
    task_id: str,
    reason: str,
    risk: str,
    action_required: str,
    resume_condition: str,
    safe_to_pause: bool = True,
) -> None:
    """Open a HUMAN_REQUIRED pause, matching the schema in
    docs/AUTONOMOUS_AGENT_PROTOCOL.md §8 exactly."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO human_required_queue
                (task_id, reason, risk, action_required, resume_condition, safe_to_pause)
            VALUES
                (%(task_id)s, %(reason)s, %(risk)s, %(action_required)s, %(resume_condition)s, %(safe_to_pause)s)
            """,
            {
                "task_id": task_id,
                "reason": reason,
                "risk": risk,
                "action_required": action_required,
                "resume_condition": resume_condition,
                "safe_to_pause": safe_to_pause,
            },
        )
        cur.execute(
            """
            UPDATE tasks
            SET human_required = true,
                human_action = %(human_action)s
            WHERE task_id = %(task_id)s
            """,
            {
                "task_id": task_id,
                "human_action": Json(
                    {
                        "reason": reason,
                        "risk": risk,
                        "action_required": action_required,
                        "system_state": {"safe_to_pause": safe_to_pause},
                        "resume_condition": resume_condition,
                    }
                ),
            },
        )
    conn.commit()


def resolve_human_required(conn: psycopg.Connection, task_id: str) -> None:
    """Clear the open pause once resume_condition is met -- the task
    resumes in the state it paused from (already recorded on the task
    row), per docs/RUNTIME_ARCHITECTURE.md §16."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE human_required_queue
            SET resolved_at = now()
            WHERE task_id = %(task_id)s AND resolved_at IS NULL
            """,
            {"task_id": task_id},
        )
        cur.execute(
            """
            UPDATE tasks
            SET human_required = false, human_action = NULL
            WHERE task_id = %(task_id)s
            """,
            {"task_id": task_id},
        )
    conn.commit()


def open_pauses(conn: psycopg.Connection) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, task_id, reason, risk, action_required, safe_to_pause, resume_condition, raised_at
            FROM human_required_queue
            WHERE resolved_at IS NULL
            ORDER BY raised_at
            """
        )
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
