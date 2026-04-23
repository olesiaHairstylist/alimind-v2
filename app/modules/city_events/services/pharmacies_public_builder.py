from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.city_events.services.pharmacies_payload import (
    build_pharmacies_payload,
    extract_raw_items,
)
APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "pharmacies_raw.json"
PUBLIC_FILE = APP_DIR / "data" / "public" / "city_events" / "duty_pharmacies_today.json"


def load_raw() -> Any:
    if not RAW_FILE.exists():
        return []

    text = RAW_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []


def save_public(payload: dict[str, Any]) -> Path:
    PUBLIC_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return PUBLIC_FILE


def build_public_from_raw() -> dict[str, Any]:
    raw_data = load_raw()

    updated_at = None
    if isinstance(raw_data, dict):
        updated_at = raw_data.get("fetched_at") or raw_data.get("updated_at")

    raw_items = extract_raw_items(raw_data)
    payload = build_pharmacies_payload(
        raw_items=raw_items,
        updated_at=updated_at,
    )

    save_public(payload)
    return payload


if __name__ == "__main__":
    result = build_public_from_raw()
    print(f"STATUS: {result.get('status', 'unknown')}")
    print(f"ITEMS: {len(result.get('items', []))}")
    print(f"PUBLIC SAVED: {PUBLIC_FILE}")