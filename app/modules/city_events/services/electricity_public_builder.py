from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.city_events.sources.electricity_builder import (
    build_electricity_payload,
    extract_raw_items,
)

BASE_DIR = Path(__file__).resolve().parents[3]

RAW_PATH = BASE_DIR / "data" / "sources" / "electricity_raw.json"
PUBLIC_PATH = BASE_DIR / "data" / "public" / "city_events" / "electricity_outages_today.json"


def read_electricity_raw() -> dict[str, Any]:
    if not RAW_PATH.exists():
        return {}

    try:
        return json.loads(RAW_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_public_payload(payload: dict[str, Any]) -> None:
    PUBLIC_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_public_from_raw() -> dict[str, Any]:
    raw_data = read_electricity_raw()

    updated_at = None
    if isinstance(raw_data, dict):
        updated_at = raw_data.get("fetched_at") or raw_data.get("updated_at")

    raw_items = extract_raw_items(raw_data)
    payload = build_electricity_payload(
        raw_items=raw_items,
        updated_at=updated_at,
    )

    write_public_payload(payload)
    return payload


if __name__ == "__main__":
    result = build_public_from_raw()
    print(f"STATUS: {result.get('status', 'unknown')}")
    print(f"ITEMS: {len(result.get('items', []))}")
    print(f"PUBLIC SAVED: {PUBLIC_PATH}")