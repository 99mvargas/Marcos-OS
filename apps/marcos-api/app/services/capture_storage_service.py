import os
import time
from datetime import datetime, timezone

from fastapi import UploadFile

from app.storage.paths import CAPTURE_CATEGORIES, capture_category_dir, ensure_data_dirs


def save_capture(category: str, file: UploadFile) -> str:
    ensure_data_dirs()
    safe_filename = os.path.basename(file.filename or "capture")
    stored_filename = f"{int(time.time() * 1000)}-{safe_filename}"
    destination = capture_category_dir(category) / stored_filename
    with destination.open("wb") as out_file:
        out_file.write(file.file.read())
    return stored_filename


def list_recent_captures(limit: int = 20) -> list[dict]:
    ensure_data_dirs()
    entries = []
    for category in CAPTURE_CATEGORIES:
        for entry in capture_category_dir(category).iterdir():
            if entry.is_file() and entry.name != ".gitkeep":
                entries.append(
                    {
                        "filename": entry.name,
                        "category": category,
                        "uploaded_at": datetime.fromtimestamp(
                            entry.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
    entries.sort(key=lambda entry: entry["uploaded_at"], reverse=True)
    return entries[:limit]
