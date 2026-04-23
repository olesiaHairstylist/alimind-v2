from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")


def now_tr_iso() -> str:
    return datetime.now(ISTANBUL_TZ).isoformat()


def extract_raw_items(raw_data: Any) -> list[dict[str, Any]]:
    """
    Извлекает raw items из pharmacies raw source.

    Допустимые входы:
    - list[dict]
    - dict с ключом "items"
    """
    if isinstance(raw_data, list):
        return [item for item in raw_data if isinstance(item, dict)]

    if isinstance(raw_data, dict):
        items = raw_data.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]

    return []


def build_pharmacies_payload(
    raw_items: list[dict[str, Any]],
    updated_at: str | None = None,
) -> dict[str, Any]:
    """
    Собирает PUBLIC payload для pharmacies.
    """

    result_items: list[dict[str, Any]] = []

    for item in raw_items:
        title = (
            str(item.get("title") or item.get("name") or "")
            .strip()
        )
        details = str(item.get("details", "")).strip()
        address = str(item.get("address", "")).strip()
        phone = str(item.get("phone", "")).strip()

        result_items.append(
            {
                "title": title,
                "details": details,
                "address": address,
                "phone": phone,
            }
        )

    status = "ok" if result_items else "empty"

    return {
        "category": "pharmacies",
        "updated_at": updated_at or now_tr_iso(),
        "status": status,
        "items": result_items,
    }