from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.modules.city_events.parsers.electricity_cards import (
    parse_electricity_items_from_raw,
)


APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "electricity_raw.json"
OUT_FILE = APP_DIR / "data" / "city_events" / "electricity_outages.json"


def load_raw() -> list[dict]:
    if not RAW_FILE.exists():
        return []

    text = RAW_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []

    data = json.loads(text)
    return data if isinstance(data, list) else []


def build_payload(items: list[dict]) -> dict:
    now_iso = datetime.now().isoformat()
    return {
        "category": "electricity",
        "updated_at": now_iso,
        "items": items,
    }


def save_payload(payload: dict) -> Path:
    print("SAVE PAYLOAD:", payload)
    print("OUT_FILE:", OUT_FILE)
    OUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return OUT_FILE


def run_build() -> Path:
    raw = load_raw()
    print("RAW COUNT:", len(raw))
    items = parse_electricity_items_from_raw(raw)
    print("PARSED ITEMS:", items)
    payload = build_payload(items)
    return save_payload(payload)


if __name__ == "__main__":
    path = run_build()
    print("WRITTEN:", path)
    print("ABS:", path.resolve())