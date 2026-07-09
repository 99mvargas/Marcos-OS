import os

from fastapi import UploadFile

from app.storage.paths import STATEMENTS_DIR, ensure_data_dirs


def save_statement(file: UploadFile) -> str:
    ensure_data_dirs()
    safe_filename = os.path.basename(file.filename or "statement")
    destination = STATEMENTS_DIR / safe_filename
    with destination.open("wb") as out_file:
        out_file.write(file.file.read())
    return safe_filename


def list_statements() -> list[str]:
    ensure_data_dirs()
    return sorted(
        entry.name for entry in STATEMENTS_DIR.iterdir() if entry.is_file() and entry.name != ".gitkeep"
    )
