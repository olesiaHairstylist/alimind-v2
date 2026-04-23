from __future__ import annotations

import json
from pathlib import Path

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.text import get_text

DATA_PATH = Path("app/data/objects")


def load_object_by_id(object_id: str) -> dict | None:
    file_path = DATA_PATH / f"{object_id}.json"

    print("DEBUG OBJECT ID:", object_id)
    print("DEBUG PATH:", file_path.resolve())

    if not file_path.exists():
        print("DEBUG ERROR: FILE NOT FOUND")
        return None

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    print("DEBUG FILE DATA:", data)
    return data


def render_object_card(obj: dict, lang: str = "ru") -> str:
    lines: list[str] = []

    title = get_text(obj.get("title"), lang) or "Без названия"
    lines.append(title)
    lines.append("")

    description = get_text(obj.get("description_short"), lang) or get_text(obj.get("description_full"), lang)
    if description:
        lines.append(description)
        lines.append("")

    location = get_text(obj.get("location"), lang)
    if location:
        lines.append(f"📍 Локация: {location}")

    contact = get_text(obj.get("contact"), lang)
    if contact:
        lines.append(f"💬 Контакт: {contact}")

    phone = obj.get("phone")
    if phone:
        lines.append(f"📞 Телефон: {phone}")

    languages = obj.get("languages", [])
    if languages:
        lines.append(f"🌐 Языки: {', '.join(languages)}")

    services = obj.get("services", [])
    if services:
        lines.append("")
        lines.append("Услуги:")
        for service in services:
            lines.append(f"• {service}")

    return "\n".join(lines)


def build_object_card_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="main:directory")
    kb.button(text="🏠 В меню", callback_data="main:menu")
    kb.adjust(1)
    return kb.as_markup()
