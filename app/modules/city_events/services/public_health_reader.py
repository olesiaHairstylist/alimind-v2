from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.modules import get_rule

BASE_DIR = Path(__file__).resolve().parents[3]
PUBLIC_DIR = BASE_DIR / "data" / "public" / "city_events"

FILES = {
    "electricity": "electricity_outages_today.json",
    "water": "water_outages_today.json",
    "pharmacies": "duty_pharmacies_today.json",
    "emergency": "emergency_contacts.json",
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _parse_dt(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _freshness_label(updated_at: str | None) -> str:
    dt = _parse_dt(updated_at)
    if dt is None:
        return "unknown"

    now = datetime.now().astimezone()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone()

    delta = now - dt.astimezone(now.tzinfo)

    hours = delta.total_seconds() / 3600

    if hours <= 12:
        return "fresh"
    if hours <= 48:
        return "aging"
    return "stale"


def _build_entry(category: str, data: dict[str, Any] | None) -> dict[str, Any]:
    rule = get_rule(category)

    if not data:
        return {
            "status": "error",
            "items_count": 0,
            "updated_at": None,
            "is_expected_empty": False,
            "freshness": "unknown",
            "error_details": "public file missing or unreadable",
        }

    raw_status = data.get("status")
    items = data.get("items") or []
    updated_at = data.get("updated_at")
    items_count = len(items) if isinstance(items, list) else 0

    status = raw_status if raw_status in ("ok", "empty", "error", "expected_empty") else "error"

    is_expected_empty = False

    if status == "empty" and items_count == 0:
        if rule.get("empty_is_expected", False):
            is_expected_empty = True

    if status == "expected_empty":
        is_expected_empty = True

    error_details = None
    if status == "error":
        error_details = data.get("error") or data.get("message") or "public status=error"

    if status == "empty" and items_count == 0 and not rule.get("empty_allowed", False):
        error_details = "empty state is not expected for this category"

    return {
        "status": status,
        "items_count": items_count,
        "updated_at": updated_at,
        "is_expected_empty": is_expected_empty,
        "freshness": _freshness_label(updated_at),
        "error_details": error_details,
    }

def read_public_health() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for key, filename in FILES.items():
        path = PUBLIC_DIR / filename
        data = _read_json(path)
        result[key] = _build_entry(key, data)

    return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(read_public_health())