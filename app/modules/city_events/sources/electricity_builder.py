from __future__ import annotations

from datetime import datetime
from typing import Any




def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None

    for fmt in ("%d/%m/%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
        try:
            return datetime.strptime(value, fmt).astimezone()
        except ValueError:
            continue

    return None


def _is_actual_item(item: dict[str, Any]) -> bool:
    details = item.get("details", "") or ""

    if "Çalışma Tamamlandı" in details:
        return False

    end_at = _parse_dt(item.get("end_at"))
    if end_at and end_at < datetime.now().astimezone():
        return False

    return True

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
    cards = [item for item in source_items if _is_actual_item(item)]

    payload: dict[str, Any] = {
        "category": "electricity",
        "updated_at": updated_at or _now_iso(),
        "status": "ok" if cards else "empty",
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