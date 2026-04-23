from __future__ import annotations

from typing import Dict, List

from app.core.text import get_text


def render_directory_category_objects(category_id: str, objects: List[Dict], lang: str = "ru") -> str:
    if not objects:
        return "Нет объектов в категории"

    category_titles = {
        "beauty": "💇 Красота",
        "services": "🛠 Услуги",
    }
    title = category_titles.get(category_id, "Категория")

    lines = [title, ""]
    for idx, obj in enumerate(objects, start=1):
        name = get_text(obj.get("title"), lang) or "Без названия"
        lines.append(f"{idx}. {name}")

    return "\n".join(lines)
