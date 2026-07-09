from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
STATEMENTS_DIR = DATA_DIR / "statements"
FINANCIAL_RECORDS_DIR = DATA_DIR / "financial-records"
RECOMMENDATIONS_DIR = DATA_DIR / "recommendations"
SETTINGS_DIR = DATA_DIR / "settings"

UPLOADS_DIR = DATA_DIR / "uploads"
CAPTURE_CATEGORIES = ("ideas", "receipts", "statements", "photos")


def capture_category_dir(category: str) -> Path:
    return UPLOADS_DIR / category


def ensure_data_dirs() -> None:
    for directory in (
        STATEMENTS_DIR,
        FINANCIAL_RECORDS_DIR,
        RECOMMENDATIONS_DIR,
        SETTINGS_DIR,
        *(capture_category_dir(category) for category in CAPTURE_CATEGORIES),
    ):
        directory.mkdir(parents=True, exist_ok=True)
