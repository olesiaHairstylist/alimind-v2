from __future__ import annotations

from app.core.text import get_text
from app.modules.directory.contracts.categories import (
    get_category_title,
    get_subcategory_title,
)


def _normalize_languages(value: object) -> str:
    if not value:
        return ""

    if isinstance(value, str):
        return value.upper()

    if isinstance(value, list):
        items = [str(item).strip().upper() for item in value if str(item).strip()]
        return ", ".join(items)

    return str(value).strip().upper()


def render_object_card(obj: dict, lang: str = "ru") -> str:
    title = get_text(obj.get("title"), lang).strip()

    category_id = str(obj.get("category", "")).strip()
    subcategory_id = str(obj.get("subcategory", "")).strip()

    category_title = get_category_title(category_id, lang) if category_id else ""
    subcategory_title = (
        get_subcategory_title(subcategory_id, lang) if subcategory_id else ""
    )

    description_full = get_text(obj.get("description_full"), lang).strip()
    description_short = get_text(obj.get("description_short"), lang).strip()
    description = description_full or description_short

    location = get_text(obj.get("location"), lang).strip()
    contact = get_text(obj.get("contact"), lang).strip()
    languages = _normalize_languages(obj.get("languages"))

    parts: list[str] = []

    if title:
        parts.append(f"📌 {title}")

    if category_title and subcategory_title:
        parts.append(f"📂 {category_title} → {subcategory_title}")
    elif category_title:
        parts.append(f"📂 {category_title}")
    elif subcategory_title:
        parts.append(f"📂 {subcategory_title}")

    if description:
        parts.append(description)

    meta_lines: list[str] = []

    if location:
        meta_lines.append(f"📍 {location}")

    if contact:
        meta_lines.append(f"📞 {contact}")

    if languages:
        meta_lines.append(f"🌐 Languages: {languages}")

    if meta_lines:
        parts.append("\n".join(meta_lines))

    return "\n\n".join(parts).strip()