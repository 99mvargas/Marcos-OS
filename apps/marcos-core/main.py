"""Marcos Core — entry point for the Marcos OS orchestration engine."""

import sys
from pathlib import Path

# Resolve the repository root and add app root to sys.path.
_APP_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _APP_ROOT.parents[1]
_VAULT_PATH = _REPO_ROOT / "obsidian"

sys.path.insert(0, str(_APP_ROOT))

from services.daily_executive_cycle import DailyExecutiveCycle
from services.morning_brief import render_brief

_DIVIDER = "=" * 40

# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------
print(_DIVIDER)
print("MARCOS OS")
print("Daily Executive Cycle")
print(_DIVIDER)

# ---------------------------------------------------------------------------
# Execute the daily cycle
# ---------------------------------------------------------------------------
cycle = DailyExecutiveCycle(vault_path=_VAULT_PATH)
result = cycle.run()

# ---------------------------------------------------------------------------
# Print execution summary
# ---------------------------------------------------------------------------
print(f"Knowledge Documents:      {result.knowledge_documents}")
print(f"Draft Memory Objects:     {result.draft_memory_count}")
print(f"Executives Run:           {result.executives_run}")
print(f"Recommendations (total):  {result.total_recommendations}")
print(f"Recommendations (today):  {result.recommendations_selected}")
print(f"Execution Time:           {result.execution_time_ms:.0f} ms")
print(_DIVIDER)

# ---------------------------------------------------------------------------
# Print Morning Brief
# ---------------------------------------------------------------------------
if result.morning_brief:
    render_brief(
        brief=result.morning_brief,
        knowledge_documents=result.knowledge_documents,
        executives_run=result.executives_run,
        recommendations_selected=result.recommendations_selected,
    )

print(_DIVIDER)
print("System Ready")
