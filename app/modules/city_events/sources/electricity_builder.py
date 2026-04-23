from __future__ import annotations

from datetime import datetime
from typing import Any




def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def extract_raw_items(raw_data: Any) -> list[dict[str, Any]]:
    """
    Извлекает список raw items из сырого ответа источника.

    Допустимые входы:
    - list[dict]
    - dict с ключом "items"
    - dict с ключом "data"

    Ничего не нормализует.
    Ничего не решает.
    Только извлекает контейнер данных.
    """
    if isinstance(raw_data, list):
        return [item for item in raw_data if isinstance(item, dict)]

    if isinstance(raw_data, dict):
        items_value = raw_data.get("items")
        if isinstance(items_value, list):
            return [item for item in items_value if isinstance(item, dict)]

        data_value = raw_data.get("data")
        if isinstance(data_value, list):
            return [item for item in data_value if isinstance(item, dict)]

    return []


def build_electricity_payload(
    raw_items: list[dict[str, Any]] | None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """
    Собирает финальный payload для public electricity JSON.

    Выходной формат:
    {
      "category": "electricity",
      "updated_at": "...",
      "items": [
        {
          "title": "...",
          "start_at": "...",
          "end_at": "...",
          "note": "...",
          "address": "",
          "phone": ""
        }
      ]
    }
    """
    source_items = raw_items or []
    cards = build_electricity_cards(source_items)

    payload: dict[str, Any] = {
        "category": "electricity",
        "updated_at": updated_at or _now_iso(),
        "items": cards,
    }
    return payload


def build_electricity_payload_from_raw(
    raw_data: Any,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """
    Совместимая обёртка для старых вызовов.

    Принимает:
    - list[dict]
    - dict с ключом "items"
    - dict с ключом "data"

    И приводит к единому payload.
    """
    raw_items = extract_raw_items(raw_data)
    return build_electricity_payload(raw_items=raw_items, updated_at=updated_at)