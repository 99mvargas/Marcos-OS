import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. The runtime state store (TASK-0003) "
            "connection string must come from the environment, never "
            "hardcoded or committed."
        )
    return url


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """One connection per call.

    No pool: nothing calls this layer yet (TASK-0004/TASK-0005 wire up the
    first real caller), so a pool would be unused infrastructure. Revisit
    once the Orchestrator's concurrent call volume justifies one.
    """
    conn = psycopg.connect(_database_url())
    try:
        yield conn
    finally:
        conn.close()
