"""Watchdog sweep (TASK-0005).

Detects the failure modes docs/RUNTIME_ARCHITECTURE.md §15 names and that
AUTONOMOUS_AGENT_PROTOCOL.md requires escalation for instead of looping
forever: stalled/expired leases, repeated failures past the retry cap, and
workers that started but never completed. Every check here is a plain SQL
query -- no LLM call, matching docs/TOKEN_EFFICIENCY.md.

Cost/token waste (a *signal*, not an auto-pause -- docs/TOKEN_EFFICIENCY.md
"Token/cost budgets" explicitly defers a hard ceiling to a future task) is
logged as a `task_events` row, not escalated to `human_required_queue` by
itself -- escalating on cost alone with no other signal would contradict
that already-decided scope.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

import psycopg

from app.db import tasks_repo
from app.db.human_queue_repo import raise_human_required
from app.db.invocations_repo import cost_by_task

MAX_RETRY_COUNT = 3
DEAD_INVOCATION_MINUTES = 30
COST_WARN_THRESHOLD_USD = Decimal("5.00")  # audit signal only, see module docstring


@dataclass
class WatchdogReport:
    released_leases: list[str] = field(default_factory=list)
    escalated_retry_exhausted: list[str] = field(default_factory=list)
    marked_dead_invocations: list[str] = field(default_factory=list)
    cost_warnings: list[str] = field(default_factory=list)


def _tasks_past_retry_limit(conn: psycopg.Connection) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT task_id FROM tasks
            WHERE retry_count >= %(max_retry)s AND human_required = false
              AND status NOT IN ('COMPLETED', 'CANCELLED')
            """,
            {"max_retry": MAX_RETRY_COUNT},
        )
        return [row[0] for row in cur.fetchall()]


def _dead_invocations(conn: psycopg.Connection) -> list[tuple[str, str]]:
    """Invocations still `running` long past any reasonable single-call
    duration -- the worker process crashed or was killed without the
    wrapper's own except-block running (e.g. OOM-killed), so nothing called
    `complete_invocation`."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT invocation_id, task_id FROM agent_invocations
            WHERE status = 'running'
              AND started_at < now() - %(minutes)s * interval '1 minute'
            """,
            {"minutes": DEAD_INVOCATION_MINUTES},
        )
        return [(str(row[0]), row[1]) for row in cur.fetchall()]


def _mark_invocation_dead(conn: psycopg.Connection, invocation_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE agent_invocations
            SET status = 'failed', error = 'watchdog: no completion after timeout window', completed_at = now()
            WHERE invocation_id = %(id)s AND status = 'running'
            """,
            {"id": invocation_id},
        )
    conn.commit()


def run_watchdog_sweep(conn: psycopg.Connection) -> WatchdogReport:
    report = WatchdogReport()

    report.released_leases = tasks_repo.release_expired_leases(conn)

    for task_id in _tasks_past_retry_limit(conn):
        raise_human_required(
            conn,
            task_id=task_id,
            reason="INVOCATION_FAILURE",
            risk="LOW",
            action_required=(
                f"{task_id} has exhausted its {MAX_RETRY_COUNT}-attempt retry budget "
                "(docs/RUNTIME_ARCHITECTURE.md §14). Review why it keeps failing -- "
                "likely mis-scoped, not under-resourced -- before resuming."
            ),
            resume_condition="Task is re-scoped or manually resumed after root-causing the repeated failure.",
        )
        report.escalated_retry_exhausted.append(task_id)

    for invocation_id, task_id in _dead_invocations(conn):
        _mark_invocation_dead(conn, invocation_id)
        report.marked_dead_invocations.append(invocation_id)
        tasks_repo.record_event(
            conn, task_id, actor="Watchdog", event_type="dead_invocation_detected",
            detail={"invocation_id": invocation_id, "timeout_minutes": DEAD_INVOCATION_MINUTES},
        )

    # Cost audit signal (docs/TOKEN_EFFICIENCY.md "How to detect token
    # waste") -- logged, not escalated; see module docstring.
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT task_id FROM agent_invocations")
        task_ids = [row[0] for row in cur.fetchall()]
    for task_id in task_ids:
        totals = cost_by_task(conn, task_id)
        if Decimal(str(totals["total_estimated_cost_usd"])) > COST_WARN_THRESHOLD_USD:
            tasks_repo.record_event(
                conn, task_id, actor="Watchdog", event_type="cost_warning",
                detail={"total_estimated_cost_usd": str(totals["total_estimated_cost_usd"])},
            )
            report.cost_warnings.append(task_id)

    return report
