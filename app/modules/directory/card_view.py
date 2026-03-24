import json
import os

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

DATA_PATH = "app/data/objects"


def load_object_by_id(object_id: str):
    filename = f"{object_id}.json"
    full_path = os.path.join(DATA_PATH, filename)

    if not os.path.exists(full_path):
        return None

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_object_card(obj: dict) -> str:
    lines = []

    lines.append(obj.get("title", "Без названия"))
    lines.append("")

    description_full = obj.get("description_full")
    if description_full:
        lines.append(description_full)
        lines.append("")

    location = obj.get("location")
    if location:
        lines.append(f"📍 Локация: {location}")

    contact = obj.get("contact")
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