from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path("app/data/objects/directory_subcategories.json")


def load_subcategories_by_category(category_id: str) -> list[dict]:
    if not DATA_PATH.exists():
        return []

    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    items = data.get(category_id)

    if not isinstance(items, list):
        return []

    result: list[dict] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        subcategory_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()

        if not subcategory_id or not title:
            continue

        result.append(
            {
                "id": subcategory_id,
                "title": title,
            }
        )

    return result