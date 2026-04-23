from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.city_events.contracts.categories import CityEventCategory

CATEGORY_FILE_MAP: dict[CityEventCategory, str] = {
    CityEventCategory.PHARMACIES: "duty_pharmacies.json",
    CityEventCategory.ELECTRICITY: "electricity_outages.json",
    CityEventCategory.WATER: "water_outages.json",
    CityEventCategory.EMERGENCY: "emergency_contacts.json",
}


def read_payload(data_dir: Path, category: CityEventCategory) -> dict[str, Any] | None:
    filename = CATEGORY_FILE_MAP.get(category)
    if filename is None:
        return None

    file_path = data_dir / filename
    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        return None

    items = raw.get("items", [])
    if not isinstance(items, list):
        items = []

    normalized_items: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized_items.append(
            {
                "title": str(item.get("title", "")).strip(),
                "details": str(item.get("details", "")).strip(),
                "address": str(item.get("address", "")).strip(),
                "phone": str(item.get("phone", "")).strip(),
            }
        )

    return {
        "category": str(raw.get("category", category.value)).strip(),
        "updated_at": str(raw.get("updated_at", "")).strip(),
        "items": normalized_items,
    }