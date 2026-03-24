from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.city_events.contracts.categories import CityEventCategory


@dataclass(slots=True)
class CityEventItem:
    title: str
    details: str = ""
    address: str = ""
    phone: str = ""


@dataclass(slots=True)
class CityEventPayload:
    category: CityEventCategory
    updated_at: str
    items: list[CityEventItem] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.items) == 0


def item_to_dict(item: CityEventItem) -> dict[str, str]:
    return {
        "title": item.title,
        "details": item.details,
        "address": item.address,
        "phone": item.phone,
    }


def item_from_dict(data: dict[str, Any]) -> CityEventItem:
    return CityEventItem(
        title=str(data.get("title", "")).strip(),
        details=str(data.get("details", "")).strip(),
        address=str(data.get("address", "")).strip(),
        phone=str(data.get("phone", "")).strip(),
    )


def payload_to_dict(payload: CityEventPayload) -> dict[str, Any]:
    return {
        "category": payload.category.value,
        "updated_at": payload.updated_at,
        "items": [item_to_dict(item) for item in payload.items],
    }


def payload_from_dict(data: dict[str, Any]) -> CityEventPayload:
    raw_category = str(data.get("category", "")).strip()
    raw_updated_at = str(data.get("updated_at", "")).strip()
    raw_items = data.get("items", [])

    if not isinstance(raw_items, list):
        raw_items = []

    return CityEventPayload(
        category=CityEventCategory(raw_category),
        updated_at=raw_updated_at,
        items=[item_from_dict(item) for item in raw_items if isinstance(item, dict)],
    )