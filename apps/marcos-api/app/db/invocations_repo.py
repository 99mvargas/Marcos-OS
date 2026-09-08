from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import class_row
from psycopg.types.json import Json

from app.db.cost import estimate_cost_usd
from app.db.models import AgentInvocation


def start_invocation(
    conn: psycopg.Connection,
    invocation_id: UUID,
    task_id: str,
    role: str,
    provider: str,
    model: str | None = None,
) -> None:
    """Record an invocation attempt before dispatch.

    invocation_id doubles as the idempotency key
    (docs/RUNTIME_ARCHITECTURE.md §14): the caller generates it before the
    invocation starts, so a retried dispatch reuses the same id instead of
    creating a second row -- the caller should check for an existing row
    with this id (via get_invocation) before calling start_invocation again.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO agent_invocations
                (invocation_id, task_id, role, provider, model, status, started_at)
            VALUES
                (%(invocation_id)s, %(task_id)s, %(role)s, %(provider)s, %(model)s, 'running', now())
            """,
            {
                "invocation_id": invocation_id,
                "task_id": task_id,
                "role": role,
                "provider": provider,
                "model": model,
            },
        )
    conn.commit()


def complete_invocation(
    conn: psycopg.Connection,
    invocation_id: UUID,
    status: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    duration_ms: int | None = None,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    """Record the outcome of an invocation, including the token/cost
    telemetry TASK-0003 requires every invocation to capture."""
    with conn.cursor(row_factory=class_row(AgentInvocation)) as cur:
        cur.execute(
            "SELECT * FROM agent_invocations WHERE invocation_id = %(id)s",
            {"id": invocation_id},
        )
        existing = cur.fetchone()

    provider = existing.provider if existing else None
    model = existing.model if existing else None
    total_tokens = None
    if input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    estimated_cost = estimate_cost_usd(provider or "", model, input_tokens, output_tokens)

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_invocations
            SET status = %(status)s,
                input_tokens = %(input_tokens)s,
                output_tokens = %(output_tokens)s,
                total_tokens = %(total_tokens)s,
                estimated_cost_usd = %(estimated_cost_usd)s,
                duration_ms = %(duration_ms)s,
                completed_at = now(),
                result = %(result)s,
                error = %(error)s
            WHERE invocation_id = %(invocation_id)s
            """,
            {
                "invocation_id": invocation_id,
                "status": status,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": estimated_cost,
                "duration_ms": duration_ms,
                "result": Json(result) if result is not None else None,
                "error": error,
            },
        )
    conn.commit()


def get_invocation(conn: psycopg.Connection, invocation_id: UUID) -> AgentInvocation | None:
    with conn.cursor(row_factory=class_row(AgentInvocation)) as cur:
        cur.execute(
            "SELECT * FROM agent_invocations WHERE invocation_id = %(id)s",
            {"id": invocation_id},
        )
        return cur.fetchone()


def cost_by_task(conn: psycopg.Connection, task_id: str) -> dict[str, Any]:
    """Aggregate token/cost telemetry for one task -- the per-task audit
    query described in docs/TOKEN_EFFICIENCY.md."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                count(*) AS invocation_count,
                coalesce(sum(input_tokens), 0) AS total_input_tokens,
                coalesce(sum(output_tokens), 0) AS total_output_tokens,
                coalesce(sum(estimated_cost_usd), 0) AS total_estimated_cost_usd
            FROM agent_invocations
            WHERE task_id = %(task_id)s
            """,
            {"task_id": task_id},
        )
        row = cur.fetchone()
    columns = ["invocation_count", "total_input_tokens", "total_output_tokens", "total_estimated_cost_usd"]
    return dict(zip(columns, row)) if row else dict.fromkeys(columns, 0)
