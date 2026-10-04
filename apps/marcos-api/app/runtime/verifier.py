"""Independent, deterministic verification (TASK-0005).

Per docs/AUTONOMOUS_AGENT_PROTOCOL.md §11, a task only reaches `CHECKPOINT`
after the Builder's own self-report is checked by something that isn't the
Builder. The checks here are plain code -- no LLM call, per
docs/TOKEN_EFFICIENCY.md's "deterministic operations must never consume an
LLM call" rule -- and run *in addition to*, not instead of, the adversarial
Reviewer-role worker invocation (`claude_worker.invoke_claude`/
`codex_worker.invoke_codex` with `role="Reviewer"`), which is where genuine
code-quality judgment belongs.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

_SECRET_PATTERNS = (
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9/_+.\-]{12,}['\"]"),
    re.compile(r"(?i)(secret|password|passwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]"),
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----"),
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id shape
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # common LLM API key shape
)


@dataclass
class VerificationResult:
    passed: bool
    checks: list[dict] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            self.passed = False


def _git_status_files(cwd: str) -> set[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, timeout=30
    )
    return {line[3:].strip() for line in out.stdout.splitlines() if line.strip()}


def scan_for_secrets(cwd: str, files: list[str]) -> list[str]:
    """Returns the subset of `files` that match a secret-like pattern.
    Pattern-based, not a guarantee -- a human reviewing a real secret leak
    should never rely on this alone (same caveat Repository B's AGENTS.md
    makes about its own redaction filters)."""
    flagged = []
    for rel_path in files:
        try:
            with open(f"{cwd}/{rel_path}", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            continue
        if any(p.search(content) for p in _SECRET_PATTERNS):
            flagged.append(rel_path)
    return flagged


def unintended_changes(cwd: str, declared_files_changed: list[str]) -> list[str]:
    """Files touched in the working tree that the Builder did not declare
    in `files_changed` -- scope-creep detection, per
    AUTONOMOUS_AGENT_PROTOCOL.md §11's "unnecessary complexity relative to
    what the task required" / AGENT_ROLES.md's "doesn't silently expand
    scope" checks."""
    actual = _git_status_files(cwd)
    declared = set(declared_files_changed)
    return sorted(actual - declared)


def run_test_commands(cwd: str, commands: list[str], timeout_s: int = 300) -> list[dict]:
    """Actually runs the declared test commands -- real execution, not a
    static read of the diff, per AGENT_ROLES.md's Tester standard. Each
    command is plain shell; this is a deterministic subprocess call, not an
    LLM invocation."""
    results = []
    for command in commands:
        try:
            proc = subprocess.run(
                command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout_s
            )
            results.append(
                {
                    "command": command,
                    "result": "PASS" if proc.returncode == 0 else "FAIL",
                    "exit_code": proc.returncode,
                    "stderr_tail": proc.stderr[-2000:],
                }
            )
        except subprocess.TimeoutExpired:
            results.append({"command": command, "result": "FAIL", "exit_code": -1, "stderr_tail": "timeout"})
    return results


def verify(
    *,
    cwd: str,
    files_changed: list[str],
    test_commands: list[str] | None = None,
) -> VerificationResult:
    """The one entry point the Orchestrator calls before accepting a
    Builder/Tester result as checkpoint-ready. Never mutates anything."""
    result = VerificationResult(passed=True)

    secret_hits = scan_for_secrets(cwd, files_changed)
    result.add("no_secrets_in_changed_files", not secret_hits, detail=", ".join(secret_hits))

    extra = unintended_changes(cwd, files_changed)
    result.add("no_unintended_changes", not extra, detail=", ".join(extra))

    if test_commands:
        test_results = run_test_commands(cwd, test_commands)
        all_passed = all(t["result"] == "PASS" for t in test_results)
        result.add(
            "declared_tests_pass",
            all_passed,
            detail="; ".join(f"{t['command']}: {t['result']}" for t in test_results),
        )

    return result
