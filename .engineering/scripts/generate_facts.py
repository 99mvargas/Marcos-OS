#!/usr/bin/env python3
"""Scan the repository and write .engineering/facts.json.

facts.json holds only machine-derived information. Never hand-edit it —
re-run this script (or `generate.py`) instead. Standard library only.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".engineering" / "facts.json"
GENERATOR_VERSION = "1.0.0"

IGNORE_SEGMENTS = {
    "node_modules", ".venv", "__pycache__", "dist", ".git",
    "jellyfin-cache", "jellyfin-config",
}
ALWAYS_INCLUDE_HIDDEN = {".claude", ".engineering", ".context", ".github"}
HIGHLIGHT_LIBS = ["react", "vite", "tailwindcss", "react-router-dom", "fastapi", "uvicorn"]

_sources: list[str] = []


def _track(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    if rel not in _sources:
        _sources.append(rel)


def _read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    _track(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def scan_dashboard_stack(pkg_json: Path) -> list[str]:
    text = _read_text(pkg_json)
    if not text:
        return []
    data = json.loads(text)
    return sorted(set(data.get("dependencies", {})) | set(data.get("devDependencies", {})))


def scan_python_stack(requirements_txt: Path) -> list[str]:
    text = _read_text(requirements_txt)
    if not text:
        return []
    return [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def scan_endpoints(app_dir: Path) -> list[str]:
    pattern = re.compile(r'@(?:router|app)\.(get|post|put|delete|patch)\("([^"]+)"')
    endpoints: set[str] = set()
    if not app_dir.exists():
        return []
    for py_file in sorted(app_dir.rglob("*.py")):
        if any(seg in IGNORE_SEGMENTS for seg in py_file.parts):
            continue
        text = _read_text(py_file)
        if not text:
            continue
        for method, path in pattern.findall(text):
            endpoints.add(f"{method.upper()} {path}")
    return sorted(endpoints)


def scan_dashboard_routes(app_tsx: Path) -> list[str]:
    text = _read_text(app_tsx)
    if not text:
        return []
    return sorted(set(re.findall(r'<Route\s+path="([^"]+)"', text)))


def scan_docker_services() -> list[dict]:
    docker_dir = ROOT / "docker"
    if not docker_dir.exists():
        return []
    _track(docker_dir)
    services: list[dict] = []
    for compose_file in sorted(docker_dir.glob("docker-compose*.yml")):
        text = _read_text(compose_file)
        if not text:
            continue
        current = None
        in_services = False
        in_ports = False
        for line in text.splitlines():
            if line.startswith("services:"):
                in_services = True
                continue
            if not in_services:
                continue
            if line and not line.startswith(" ") and not line.startswith("services:"):
                break
            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()
            if indent == 2 and stripped.endswith(":"):
                if current:
                    services.append(current)
                current = {
                    "name": stripped[:-1],
                    "image": None,
                    "ports": [],
                    "source": str(compose_file.relative_to(ROOT)),
                }
                in_ports = False
                continue
            if current is None:
                continue
            if stripped.startswith("image:"):
                current["image"] = stripped.split("image:", 1)[1].strip()
            elif stripped == "ports:":
                in_ports = True
            elif in_ports and stripped.startswith("-"):
                current["ports"].append(stripped.lstrip("- ").strip('"'))
            elif stripped.endswith(":"):
                in_ports = False
        if current:
            services.append(current)
    return services


def scan_service_registry(registry_ts: Path) -> list[dict]:
    text = _read_text(registry_ts)
    if not text:
        return []
    entries = []
    for block in re.findall(r"\{([^{}]*)\}", text):
        id_m = re.search(r'id:\s*"([^"]+)"', block)
        name_m = re.search(r'name:\s*"([^"]+)"', block)
        url_m = re.search(r'url:\s*"([^"]+)"', block)
        if id_m and url_m:
            entries.append({
                "id": id_m.group(1),
                "name": name_m.group(1) if name_m else None,
                "url": url_m.group(1),
            })
    return entries


def scan_engineering_platform() -> dict:
    def names(dir_path: Path) -> list[str]:
        if not dir_path.exists():
            return []
        _track(dir_path)
        return sorted(p.name for p in dir_path.iterdir() if p.is_file())

    return {
        "agents": names(ROOT / ".claude" / "agents"),
        "skills": names(ROOT / ".claude" / "skills"),
        "commands": names(ROOT / ".claude" / "commands"),
    }


def scan_major_directories() -> list[dict]:
    dirs = []
    for p in sorted(ROOT.iterdir()):
        if not p.is_dir():
            continue
        if p.name == ".git":
            continue
        if p.name.startswith(".") and p.name not in ALWAYS_INCLUDE_HIDDEN:
            continue
        file_count = sum(
            1 for f in p.rglob("*")
            if f.is_file() and not any(seg in IGNORE_SEGMENTS for seg in f.parts)
        )
        has_readme = any((p / n).exists() for n in ("README.md", "readme.md"))
        dirs.append({
            "path": f"{p.relative_to(ROOT)}/",
            "file_count": file_count,
            "has_readme": has_readme,
        })
    return dirs


def scan_code_markers() -> dict:
    placeholder_files: list[str] = []
    todo_count = 0
    hardcoded_ips: set[str] = set()
    ip_pattern = re.compile(r'https?://\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?')
    for base in (ROOT / "apps" / "marcos-dashboard" / "src", ROOT / "apps" / "marcos-api" / "app"):
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file() or f.suffix not in {".py", ".ts", ".tsx"}:
                continue
            if any(seg in IGNORE_SEGMENTS for seg in f.parts):
                continue
            text = _read_text(f)
            if not text:
                continue
            if "Placeholder" in text:
                placeholder_files.append(str(f.relative_to(ROOT)))
            todo_count += len(re.findall(r"\bTODO\b", text))
            hardcoded_ips.update(ip_pattern.findall(text))
    return {
        "placeholder_files": placeholder_files,
        "todo_count": todo_count,
        "hardcoded_ip_urls": sorted(hardcoded_ips),
    }


def summarize_stack(stack: list[str]) -> str:
    lowered = {re.split(r"[\[>=<]", s, 1)[0].strip().lower(): s for s in stack}
    hits = [lowered[h] for h in HIGHLIGHT_LIBS if h in lowered]
    if hits:
        rest = len(stack) - len(hits)
        return ", ".join(hits) + (f" (+{rest} more)" if rest > 0 else "")
    return f"{len(stack)} dependencies" if stack else "no manifest found"


def scan_apps() -> dict:
    dashboard_stack = scan_dashboard_stack(ROOT / "apps" / "marcos-dashboard" / "package.json")
    api_stack = scan_python_stack(ROOT / "apps" / "marcos-api" / "requirements.txt")
    core_stack = scan_python_stack(ROOT / "apps" / "marcos-core" / "requirements.txt")
    return {
        "marcos-dashboard": {
            "path": "apps/marcos-dashboard/",
            "type": "frontend",
            "stack": dashboard_stack,
            "stack_summary": summarize_stack(dashboard_stack),
            "routes": scan_dashboard_routes(ROOT / "apps" / "marcos-dashboard" / "src" / "App.tsx"),
        },
        "marcos-api": {
            "path": "apps/marcos-api/",
            "type": "backend",
            "stack": api_stack,
            "stack_summary": summarize_stack(api_stack),
            "endpoints": scan_endpoints(ROOT / "apps" / "marcos-api" / "app"),
        },
        "marcos-core": {
            "path": "apps/marcos-core/",
            "type": "backend",
            "stack": core_stack,
            "stack_summary": summarize_stack(core_stack),
        },
    }


def main() -> dict:
    facts = {
        "apps": scan_apps(),
        "docker_services": scan_docker_services(),
        "service_registry": scan_service_registry(
            ROOT / "apps" / "marcos-dashboard" / "src" / "data" / "service-registry.ts"
        ),
        "engineering_platform": scan_engineering_platform(),
        "major_directories": scan_major_directories(),
        "code_markers": scan_code_markers(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_version": GENERATOR_VERSION,
        "sources": sorted(_sources),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
    return facts


if __name__ == "__main__":
    main()
