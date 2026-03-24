import json
import os

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

DATA_PATH = "app/data/objects"


def load_objects():
    objects = []

    if not os.path.exists(DATA_PATH):
        return objects

    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".json"):
            full_path = os.path.join(DATA_PATH, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                objects.append(json.load(f))

    return objects


def build_object_list(category: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    objects = load_objects()

    for obj in objects:
        if obj.get("category") == category:
            kb.button(
                text=obj.get("title", "Без названия"),
                callback_data=f"obj:{obj.get('id')}"
            )

    kb.button(text="⬅️ Назад", callback_data="main:directory")

    kb.adjust(1)
    return kb.as_markup()