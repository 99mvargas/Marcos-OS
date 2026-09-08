import psycopg


def record_checkpoint(conn: psycopg.Connection, task_id: str, branch: str, commit_sha: str, pushed: bool) -> None:
    """Idempotent per docs/RUNTIME_ARCHITECTURE.md §14: UNIQUE(commit_sha)
    means a retried checkpoint step either inserts a new row (new commit)
    or no-ops (ON CONFLICT DO NOTHING) rather than double-recording."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO checkpoints (task_id, branch, commit_sha, pushed)
            VALUES (%(task_id)s, %(branch)s, %(commit_sha)s, %(pushed)s)
            ON CONFLICT (commit_sha) DO NOTHING
            """,
            {"task_id": task_id, "branch": branch, "commit_sha": commit_sha, "pushed": pushed},
        )
    conn.commit()
