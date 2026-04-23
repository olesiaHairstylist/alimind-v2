from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path("app/data/objects")


def load_all_objects() -> list[dict]:
    items: list[dict] = []

    for path in DATA_PATH.glob("*.json"):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue

    return items


def load_subcategories(category_id: str) -> list[str]:
    result: list[str] = []

    for obj in load_all_objects():
        if obj.get("category") == category_id:
            subcategory_id = str(obj.get("subcategory", "")).strip()
            if subcategory_id and subcategory_id not in result:
                result.append(subcategory_id)

    return result


def load_objects_by_subcategory(subcategory_id: str) -> list[dict]:
    return [
        obj for obj in load_all_objects()
        if obj.get("subcategory") == subcategory_id
    ]


def load_object_by_id(object_id: str) -> dict | None:
    path = DATA_PATH / f"{object_id}.json"

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None