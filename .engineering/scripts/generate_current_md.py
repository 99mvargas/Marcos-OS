#!/usr/bin/env python3
"""Generate .context/current.md entirely from .engineering/context.json.

Resolves context.json's refs (facts.json, repository.json) to fill in the
Architecture/Services sections. Never reads PROJECT_STATE.md, HANDOFF.md,
NEXT_TASK.md, or VISION.md directly -- current.md is a JSON-sourced view
only. Standard library only.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTEXT = ROOT / ".engineering" / "context.json"
OUT = ROOT / ".context" / "current.md"


def _load(rel_path: str) -> dict:
    p = ROOT / rel_path
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def render_architecture(facts: dict, repository: dict) -> str:
    lines = []
    apps = facts.get("apps", {})
    repo_apps = repository.get("apps", {})
    for name in sorted(apps):
        f = apps[name]
        r = repo_apps.get(name, {})
        detail = f"`{f.get('path', name + '/')}` -- {r.get('type', f.get('type', ''))}, {f.get('stack_summary', '')}"
        if f.get("endpoints"):
            detail += f"; {len(f['endpoints'])} API endpoint(s)"
        if f.get("routes"):
            detail += f"; {len(f['routes'])} route(s)"
        if r.get("status"):
            detail += f" ({r['status']})"
        lines.append(f"- {detail}")

    ep = facts.get("engineering_platform", {})
    if ep:
        lines.append(
            f"- `.claude/` -- engineering platform: {len(ep.get('agents', []))} agents, "
            f"{len(ep.get('skills', []))} skills, {len(ep.get('commands', []))} commands."
        )

    docker_services = facts.get("docker_services", [])
    if docker_services:
        names = ", ".join(s["name"] for s in docker_services)
        lines.append(f"- Infrastructure -- Docker Compose ({names}).")

    return "\n".join(lines) if lines else "- No architecture facts available."


def render_services(repository: dict) -> str:
    lines = []
    apps = repository.get("apps", {})

    dashboard = apps.get("marcos-dashboard")
    if dashboard:
        lines.append(f"- Marcos Dashboard -- dev server, {dashboard.get('status', 'status unknown')}")

    api = apps.get("marcos-api")
    if api:
        lines.append(f"- Marcos API -- :{api.get('port', '?')}, {api.get('status', 'status unknown')}")

    infra = repository.get("infrastructure", {}).get("services", {})
    for name, svc in infra.items():
        label = name.replace("_", " ").title()
        suffix = " (external)" if svc.get("containerized") is False else ""
        lines.append(f"- {label} -- :{svc.get('port')}{suffix}")

    return "\n".join(lines) if lines else "- No service facts available."


def render_decisions(context: dict) -> str:
    decisions = context.get("decisions_awaiting_approval", [])
    if not decisions:
        return "- None."
    return "\n".join(
        f"- {d['topic']} -- awaiting {d['owner']}. Full detail in `{d['detail_ref']}`."
        for d in decisions
    )


def main() -> str:
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    facts = _load(context["refs"]["facts"])
    repository = _load(context["refs"]["architecture"])

    sprint = context["sprint"]
    task = context["task"]

    md = f"""<!-- GENERATED VIEW. Source of truth is .engineering/context.json (and the
     files it references). Do not hand-edit -- regenerate via
     `python .engineering/scripts/generate.py` instead, so this file cannot
     drift out of sync with the JSON. -->

# Current Context

## Current Sprint
{sprint['number']} -- {sprint['name']}

## Current Task
{task['summary']} Status: {task['status']}.

## Current Architecture
_Resolved from `.engineering/facts.json` (generated) and `.engineering/repository.json` (hand-maintained)._
{render_architecture(facts, repository)}

## Current Services
_Resolved from `.engineering/repository.json`._
{render_services(repository)}

## Outstanding Decisions
_From `.engineering/context.json` -> `decisions_awaiting_approval`._
{render_decisions(context)}

## Next Action
{context['next_action']}

---
Last generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} by `generate_current_md.py`, from
`.engineering/context.json` (facts resolved via `facts.json`, architecture/
services detail via `repository.json`). Markdown docs (`PROJECT_STATE.md`,
`HANDOFF.md`, `NEXT_TASK.md`) remain authoritative for full
implementation-level detail -- this file and the JSON it's built from are
for orientation only.
"""
    OUT.write_text(md, encoding="utf-8")
    return md


if __name__ == "__main__":
    main()
