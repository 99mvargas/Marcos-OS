"""Bounded, headless Claude Code invocation (TASK-0004).

Builds and runs a non-interactive `claude -p` subprocess scoped to one task,
one repo checkout, and one role-specific permission profile
(`permissions.py`). Returns a `WorkerResult` -- callers never need to parse
prose; the full raw stdout/stderr is saved to `raw_output_path` for audit,
not returned inline, per docs/TOKEN_EFFICIENCY.md's context-minimization
rules.

CLI flag choices here are empirically verified against this installed
`claude` build (2026-10-04), not assumed -- see `permissions.py`'s module
docstring for what was tested and why `bypassPermissions` is never used.
"""
from __future__ import annotations

import json
import subprocess
import time
import uuid
from pathlib import Path

from app.db.cost import estimate_cost_usd
from app.runtime.permissions import claude_profile
from app.runtime.worker_result import WorkerResult

DEFAULT_TIMEOUT_S = 900
DEFAULT_RUN_LOG_DIR = Path("/tmp/marcos-os-worker-runs")


def _git_diff_files(cwd: str, before: set[str] | None) -> list[str]:
    """Deterministic post-processing, not an LLM call (docs/TOKEN_EFFICIENCY.md):
    diff the repo's changed files before/after a Builder invocation."""
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


def invoke_claude(
    *,
    task_id: str,
    role: str,
    prompt: str,
    cwd: str,
    model: str = "claude-haiku-4-5",
    max_budget_usd: float | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    run_log_dir: Path = DEFAULT_RUN_LOG_DIR,
) -> WorkerResult:
    profile = claude_profile(role)
    run_log_dir.mkdir(parents=True, exist_ok=True)
    raw_output_path = run_log_dir / f"{task_id}-{role}-{uuid.uuid4().hex[:8]}.jsonl"

    # The target repo's own CLAUDE.md auto-loads regardless of role (verified
    # 2026-10-04: a Researcher-profile invocation still narrated itself as
    # "Chief Builder"). Append-don't-replace an explicit role statement so the
    # invocation can't confuse this call's role with the repo's default
    # persona -- the tool allowlist is still the actual enforcement.
    role_system_prompt = (
        f"For this invocation you are acting specifically as the {role} role "
        f"of the Marcos OS Autonomous Agent Protocol (docs/AGENT_ROLES.md), "
        f"working on {task_id}. Follow that role's allowed/prohibited actions "
        f"exactly, regardless of any other persona described in this "
        f"repository's CLAUDE.md."
    )

    cmd = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "json",
        "--model",
        model,
        "--tools",
        ",".join(profile.tools),
        "--append-system-prompt",
        role_system_prompt,
        "--no-session-persistence",
    ]
    if profile.disallowed_bash_patterns:
        cmd += ["--disallowedTools", *profile.disallowed_bash_patterns]
    if profile.permission_mode:
        cmd += ["--permission-mode", profile.permission_mode]
    if max_budget_usd is not None:
        cmd += ["--max-budget-usd", str(max_budget_usd)]

    before = _git_status_snapshot(cwd) if role == "Builder" else None
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        raw_output_path.write_text(
            f"TIMEOUT after {timeout_s}s\nstdout so far:\n{exc.stdout or ''}\nstderr:\n{exc.stderr or ''}"
        )
        return WorkerResult(
            task_id=task_id,
            role=role,
            provider="claude-code",
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
            provider="claude-code",
            model=model,
            status="failure",
            summary=f"claude -p exited {proc.returncode}",
            duration_ms=duration_ms,
            exit_code=proc.returncode,
            error=(proc.stderr.strip()[:2000] or None),
            raw_output_path=str(raw_output_path),
        )

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return WorkerResult(
            task_id=task_id,
            role=role,
            provider="claude-code",
            model=model,
            status="failure",
            summary="claude -p did not return valid JSON",
            duration_ms=duration_ms,
            exit_code=proc.returncode,
            error=str(exc),
            raw_output_path=str(raw_output_path),
        )

    usage = payload.get("usage") or {}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    is_error = bool(payload.get("is_error"))
    files_changed = _git_diff_files(cwd, before) if role == "Builder" else []

    return WorkerResult(
        task_id=task_id,
        role=role,
        provider="claude-code",
        model=payload.get("model") or model,
        status="failure" if is_error else "success",
        summary=str(payload.get("result", ""))[:4000],
        files_changed=files_changed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=(
            float(payload["total_cost_usd"]) if payload.get("total_cost_usd") is not None else
            (float(c) if (c := estimate_cost_usd("claude-code", payload.get("model") or model, input_tokens, output_tokens)) is not None else None)
        ),
        duration_ms=duration_ms,
        exit_code=proc.returncode,
        permission_denials=payload.get("permission_denials") or [],
        raw_output_path=str(raw_output_path),
    )
