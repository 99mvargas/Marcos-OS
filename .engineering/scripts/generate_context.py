#!/usr/bin/env python3
"""Generate .engineering/context.json entirely from facts.json + decisions.json.

context.json is generated output. Never hand-edit it — edit decisions.json
(human judgment) or let generate_facts.py rescan the repo (machine facts)
instead, then re-run this script. Standard library only.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACTS = ROOT / ".engineering" / "facts.json"
DECISIONS = ROOT / ".engineering" / "decisions.json"
OUT = ROOT / ".engineering" / "context.json"
GENERATOR_VERSION = "1.0.0"


def main() -> dict:
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    apps = facts.get("apps", {})

    context = {
        "sprint": decisions["sprint"],
        "task": decisions["task"],
        "decisions_awaiting_approval": decisions["decisions_awaiting_approval"],
        "architecture_decisions": decisions.get("architecture_decisions", []),
        "next_action": decisions["next_action"],
        "facts_summary": {
            "apps": sorted(apps.keys()),
            "api_endpoint_count": len(apps.get("marcos-api", {}).get("endpoints", [])),
            "dashboard_route_count": len(apps.get("marcos-dashboard", {}).get("routes", [])),
            "docker_service_count": len(facts.get("docker_services", [])),
            "service_registry_count": len(facts.get("service_registry", [])),
        },
        "refs": {
            "facts": ".engineering/facts.json",
            "architecture": ".engineering/repository.json",
            "executives": ".engineering/executives.json",
            "workflows": ".engineering/workflows.json",
            "commands": ".engineering/commands.json",
            "metrics": ".engineering/metrics.json",
            "full_state_markdown": ["PROJECT_STATE.md", "HANDOFF.md", "NEXT_TASK.md"],
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_version": GENERATOR_VERSION,
        "sources": [".engineering/facts.json", ".engineering/decisions.json"],
    }
    OUT.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    return context


if __name__ == "__main__":
    main()
