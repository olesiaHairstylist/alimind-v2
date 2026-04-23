from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")


def now_tr_iso() -> str:
    return datetime.now(ISTANBUL_TZ).isoformat()


def extract_raw_items(raw_data: Any) -> list[dict[str, Any]]:
    if isinstance(raw_data, list):
        return [item for item in raw_data if isinstance(item, dict)]

    if isinstance(raw_data, dict):
        items = raw_data.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]

    return []


def build_emergency_payload(
    raw_items: list[dict[str, Any]],
    updated_at: str | None = None,
) -> dict[str, Any]:
    result_items: list[dict[str, Any]] = []

    for item in raw_items:
        title = str(item.get("title") or item.get("name") or "").strip()
        details = str(item.get("details") or item.get("description") or "").strip()
        phone = str(item.get("phone") or "").strip()

        if not title and not phone:
            continue

        result_items.append(
            {
                "title": title,
                "details": details,
                "phone": phone,
            }
        )

    status = "ok" if result_items else "empty"

    return {
        "category": "emergency",
        "updated_at": updated_at or now_tr_iso(),
        "status": status,
        "items": result_items,
    }