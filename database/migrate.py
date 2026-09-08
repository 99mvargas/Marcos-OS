#!/usr/bin/env python3
"""Apply versioned SQL migrations in database/migrations/ to the runtime
state store (TASK-0003, docs/RUNTIME_ARCHITECTURE.md §6).

Deliberately not a framework (no Alembic/Flyway): the migration set is
small, forward-only, and plain SQL. This script only tracks which files
have been applied and runs the pending ones in order, each in its own
transaction.

Usage:
    DATABASE_URL=postgresql://user:pass@host:port/dbname python3 database/migrate.py
    DATABASE_URL=... python3 database/migrate.py --check   # report only, apply nothing
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def _checksum(sql_text: str) -> str:
    return hashlib.sha256(sql_text.encode("utf-8")).hexdigest()


def _migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def _ensure_tracking_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename    TEXT PRIMARY KEY,
                checksum    TEXT NOT NULL,
                applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
    conn.commit()


def _applied_filenames(conn: psycopg.Connection) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("SELECT filename, checksum FROM schema_migrations")
        return dict(cur.fetchall())


def run(database_url: str, check_only: bool) -> int:
    files = _migration_files()
    if not files:
        print("No migration files found in database/migrations/.")
        return 0

    with psycopg.connect(database_url) as conn:
        _ensure_tracking_table(conn)
        applied = _applied_filenames(conn)

        pending: list[Path] = []
        for path in files:
            sql_text = path.read_text()
            checksum = _checksum(sql_text)
            if path.name in applied:
                if applied[path.name] != checksum:
                    print(
                        f"ERROR: {path.name} was already applied but its "
                        f"content has changed since (checksum mismatch). "
                        f"Migrations are forward-only -- add a new file "
                        f"instead of editing an applied one."
                    )
                    return 1
                continue
            pending.append(path)

        if not pending:
            print(f"Up to date: {len(applied)} migration(s) already applied.")
            return 0

        print(f"{len(pending)} pending migration(s): {[p.name for p in pending]}")
        if check_only:
            return 0

        for path in pending:
            sql_text = path.read_text()
            checksum = _checksum(sql_text)
            print(f"Applying {path.name} ...")
            with conn.cursor() as cur:
                cur.execute(sql_text)
                cur.execute(
                    "INSERT INTO schema_migrations (filename, checksum) VALUES (%s, %s)",
                    (path.name, checksum),
                )
            conn.commit()
            print(f"  OK ({path.name})")

        print(f"Applied {len(pending)} migration(s).")
        return 0


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        return 1
    return run(database_url, check_only)


if __name__ == "__main__":
    raise SystemExit(main())
