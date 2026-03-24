from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.modules.city_events.contracts.categories import CityEventCategory


@dataclass
class CityEventItem:
    title: str
    details: str
    address: str
    phone: str


@dataclass
class CityEventPayload:
    category: str
    updated_at: str
    items: list[CityEventItem]


CATEGORY_FILE_MAP: dict[CityEventCategory, str] = {
    CityEventCategory.PHARMACIES: "duty_pharmacies.json",
    CityEventCategory.ELECTRICITY: "electricity_outages.json",
    CityEventCategory.WATER: "water_outages.json",
    CityEventCategory.EMERGENCY: "emergency_contacts.json",
}


def read_payload(data_dir: Path, category: CityEventCategory) -> CityEventPayload | None:
    filename = CATEGORY_FILE_MAP.get(category)
    if filename is None:
        return None

    file_path = data_dir / filename
    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    items = [
        CityEventItem(
            title=item.get("title", ""),
            details=item.get("details", ""),
            address=item.get("address", ""),
            phone=item.get("phone", ""),
        )
        for item in raw.get("items", [])
    ]

    return CityEventPayload(
        category=raw.get("category", category.value),
        updated_at=raw.get("updated_at", ""),
        items=items,
    )