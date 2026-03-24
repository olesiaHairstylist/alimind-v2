from __future__ import annotations

import json
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "water_raw.json"


def fetch_raw_data() -> list[dict]:
    """
    ВРЕМЕННО:
    сюда потом вставим реальный запрос к ASAT.
    Пока читает существующий raw, если он уже есть.
    """
    if not RAW_FILE.exists():
        return []

    text = RAW_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []

    data = json.loads(text)
    return data if isinstance(data, list) else []


def save_raw(data: list[dict]) -> Path:
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return RAW_FILE


def run_fetch() -> Path:
    data = fetch_raw_data()
    print("FETCHED:", len(data))
    return save_raw(data)


if __name__ == "__main__":
    path = run_fetch()
    print("RAW SAVED:", path)
    print("ABS:", path.resolve())