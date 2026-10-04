"""Bounded, headless Codex invocation (TASK-0004).

Mirrors `claude_worker.py`'s contract for the second provider. Builds and
runs `codex exec` scoped to one task, one repo checkout, and a role-specific
sandbox mode (`permissions.py`) -- never
`--dangerously-bypass-approvals-and-sandbox`, regardless of role.

JSONL event schema parsed here is empirically verified (2026-10-04) against
this installed `codex` build: `codex exec -s read-only --json "<prompt>"`
emits one JSON object per line -- `thread.started` (thread_id),
`turn.started`, `item.completed` (`item.type == "agent_message"` for the
model's own text), `turn.completed` (`usage`: input_tokens,
cached_input_tokens, output_tokens, reasoning_output_tokens). Codex does not
report a cost figure directly (unlike Claude Code's `total_cost_usd`); cost
is estimated from the same static pricing table TASK-0003 built
(`app/db/cost.py`), whose OpenAI/Codex rows are explicitly unverified
placeholders -- `estimated_cost_usd` is therefore `None` for Codex
invocations until that table is verified against OpenAI's published Codex
pricing (see docs/TOKEN_EFFICIENCY.md).
"""
from __future__ import annotations

import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from app.runtime.permissions import codex_profile
from app.runtime.worker_result import WorkerResult

DEFAULT_TIMEOUT_S = 900
DEFAULT_RUN_LOG_DIR = Path("/tmp/marcos-os-worker-runs")


def _git_diff_files(cwd: str, before: set[str] | None) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, timeout=30
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    after = {line[3:].strip() for line in out.stdout.splitlines() if line.strip()}
    if before is None:
        return sorted(after)
    return sorted(after - before)


def _git_status_snapshot(cwd: str) -> set[str] | None:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, timeout=30
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    return {line[3:].strip() for line in out.stdout.splitlines() if line.strip()}


def _parse_codex_jsonl(raw: str) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    """Returns (final_agent_message_text, summed_usage, error_items)."""
    summary = ""
    usage: dict[str, Any] = {}
    errors: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        if etype == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message" and item.get("text"):
                summary = item["text"]
            if item.get("type") == "error":
                errors.append(item)
        elif etype == "turn.completed":
            turn_usage = event.get("usage") or {}
            for key, value in turn_usage.items():
                if isinstance(value, (int, float)):
                    usage[key] = usage.get(key, 0) + value
        elif etype in ("turn.failed", "error"):
            errors.append(event)
    return summary, usage, errors


def invoke_codex(
    *,
    task_id: str,
    role: str,
    prompt: str,
    cwd: str,
    model: str | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    run_log_dir: Path = DEFAULT_RUN_LOG_DIR,
) -> WorkerResult:
    profile = codex_profile(role)
    run_log_dir.mkdir(parents=True, exist_ok=True)
    raw_output_path = run_log_dir / f"{task_id}-{role}-{uuid.uuid4().hex[:8]}.jsonl"

    # `codex exec` has no --append-system-prompt equivalent; prepend a role
    # preamble to the prompt itself so this invocation can't be confused with
    # the repo's default AGENTS.md persona (same rationale as
    # claude_worker.py's --append-system-prompt; see its docstring note).
    role_preamble = (
        f"For this invocation you are acting specifically as the {role} role "
        f"of the Marcos OS Autonomous Agent Protocol (docs/AGENT_ROLES.md), "
        f"working on {task_id}. Follow that role's allowed/prohibited actions "
        f"exactly, regardless of any other persona described in this "
        f"repository's AGENTS.md.\n\n"
    )

    cmd = ["codex", "exec", "-s", profile.sandbox, "-C", cwd, "--json"]
    if model:
        cmd += ["-m", model]
    cmd.append(role_preamble + prompt)

    before = _git_status_snapshot(cwd) if role == "Builder" else None
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s, stdin=subprocess.DEVNULL
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        raw_output_path.write_text(
            f"TIMEOUT after {timeout_s}s\nstdout so far:\n{exc.stdout or ''}\nstderr:\n{exc.stderr or ''}"
        )
        return WorkerResult(
            task_id=task_id,
            role=role,
            provider="codex",
            model=model,
            status="timeout",
            summary=f"Invocation exceeded {timeout_s}s timeout and was killed.",
            duration_ms=duration_ms,
            exit_code=-1,
            error="timeout",
            raw_output_path=str(raw_output_path),
        )

    duration_ms = int((time.monotonic() - started) * 1000)
    raw_output_path.write_text(proc.stdout + "\n--STDERR--\n" + proc.stderr)

    if proc.returncode != 0:
        return WorkerResult(
            task_id=task_id,
            role=role,
            provider="codex",
            model=model,
            status="failure",
            summary=f"codex exec exited {proc.returncode}",
            duration_ms=duration_ms,
            exit_code=proc.returncode,
            error=(proc.stderr.strip()[:2000] or None),
            raw_output_path=str(raw_output_path),
        )

    summary, usage, errors = _parse_codex_jsonl(proc.stdout)
    files_changed = _git_diff_files(cwd, before) if role == "Builder" else []

    return WorkerResult(
        task_id=task_id,
        role=role,
        provider="codex",
        model=model,
        status="failure" if errors else "success",
        summary=summary[:4000] if summary else (f"{len(errors)} error item(s) in transcript" if errors else ""),
        files_changed=files_changed,
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        estimated_cost_usd=None,  # app/db/cost.py's OpenAI rows are unverified placeholders -- see docstring.
        duration_ms=duration_ms,
        exit_code=proc.returncode,
        permission_denials=[],  # Codex surfaces sandbox denials as item events, not a dedicated field; not yet mapped here.
        raw_output_path=str(raw_output_path),
    )
