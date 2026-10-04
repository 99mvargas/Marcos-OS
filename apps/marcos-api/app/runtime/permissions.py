"""Role-based permission profiles for headless worker invocations (TASK-0004).

Enforces docs/RUNTIME_ARCHITECTURE.md §9's per-role tool table at the CLI-flag
level, for both supported providers. The tool allowlist -- not a permission-
mode bypass -- is the primary safety control: a tool that isn't in a role's
list is simply unavailable to the model, bypass or no bypass.

Empirically verified (2026-10-04, against this installed `claude` CLI):
- A role-scoped `--tools` allowlist alone, with no `--permission-mode` flag,
  runs a tool-using invocation to completion non-interactively -- no hang,
  no denial. Default permission mode is therefore used for every read-only
  role; no bypass flag is emitted for them.
- Builder needs file-write tools to actually write in headless mode, which
  requires `--permission-mode acceptEdits` (auto-accepts Edit/Write prompts
  only). This is deliberately *not* `bypassPermissions`/
  `--dangerously-skip-permissions`: those disable the tool-permission system
  itself for an unattended process, which this repo's own auto-mode
  classifier flags as an unsafe default for an autonomous agent loop. Bash
  commands Builder runs that would otherwise require a prompt fail closed
  (denied, surfaced in the result's `permission_denials`) rather than hang
  or silently succeed.

Known gap (v0.1, intentionally not solved here): `--tools`/`--disallowedTools`
restrict which Claude Code *tools* are offered, not what a permitted `Bash`
tool call can do once invoked -- a role with Bash access could still shell
out to something destructive. The `disallowed_bash_patterns` below block the
specific destructive patterns relevant to each role's job (push, hard reset,
rm) as defense in depth, but this is pattern matching, not a sandbox. True
isolation for Bash-bearing roles is a future task (e.g. running the
invocation inside a disposable container/VM with a read-only bind mount for
non-Builder roles), not solved by this contract.
"""
from __future__ import annotations

from dataclasses import dataclass

ROLES = ("Researcher", "Builder", "Tester", "Reviewer")


@dataclass(frozen=True)
class ClaudeProfile:
    tools: tuple[str, ...]
    disallowed_bash_patterns: tuple[str, ...]
    permission_mode: str | None  # None => omit --permission-mode (CLI default)


@dataclass(frozen=True)
class CodexProfile:
    sandbox: str  # codex exec -s value: "read-only" | "workspace-write"


_NON_BUILDER_BASH_DENYLIST = (
    "Bash(git push*)",
    "Bash(git commit*)",
    "Bash(git reset*)",
    "Bash(git clean*)",
    "Bash(rm *)",
    "Bash(mv *)",
)

_CLAUDE_PROFILES: dict[str, ClaudeProfile] = {
    "Researcher": ClaudeProfile(
        tools=("Read", "Grep", "Glob", "Bash"),
        disallowed_bash_patterns=_NON_BUILDER_BASH_DENYLIST,
        permission_mode=None,
    ),
    "Builder": ClaudeProfile(
        tools=("Read", "Grep", "Glob", "Edit", "Write", "Bash"),
        # Builder may commit/push non-main branches per AGENT_ROLES.md -- the
        # branch-name restriction is enforced by the git-engineer workflow
        # and GitHub branch protection on `main`, not by this CLI flag.
        disallowed_bash_patterns=(),
        permission_mode="acceptEdits",
    ),
    "Tester": ClaudeProfile(
        tools=("Read", "Grep", "Glob", "Bash"),
        disallowed_bash_patterns=_NON_BUILDER_BASH_DENYLIST,
        permission_mode=None,
    ),
    "Reviewer": ClaudeProfile(
        tools=("Read", "Grep", "Glob", "Bash"),
        disallowed_bash_patterns=_NON_BUILDER_BASH_DENYLIST,
        permission_mode=None,
    ),
}

_CODEX_PROFILES: dict[str, CodexProfile] = {
    "Researcher": CodexProfile(sandbox="read-only"),
    "Builder": CodexProfile(sandbox="workspace-write"),
    "Tester": CodexProfile(sandbox="read-only"),
    "Reviewer": CodexProfile(sandbox="read-only"),
}


def claude_profile(role: str) -> ClaudeProfile:
    try:
        return _CLAUDE_PROFILES[role]
    except KeyError:
        raise ValueError(f"Unknown role for a headless Claude invocation: {role!r}; expected one of {ROLES}")


def codex_profile(role: str) -> CodexProfile:
    try:
        return _CODEX_PROFILES[role]
    except KeyError:
        raise ValueError(f"Unknown role for a headless Codex invocation: {role!r}; expected one of {ROLES}")
