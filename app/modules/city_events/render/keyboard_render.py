from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.city_events.ui.callbacks import (
    CITY_EVENTS_BACK_CB,
    CITY_EVENTS_ELECTRICITY_CB,
    CITY_EVENTS_EMERGENCY_CB,
    CITY_EVENTS_PHARMACIES_CB,
    CITY_EVENTS_WATER_CB,
)


def build_city_events_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    labels = {
        "ru": {
            "pharmacies": "💊 Дежурные аптеки",
            "electricity": "🔌 Отключения электричества",
            "water": "🚰 Отключения воды",
            "emergency": "🚨 Экстренные службы",
            "main_menu": "🏠 Главное меню",
        },
        "en": {
            "pharmacies": "💊 Duty Pharmacies",
            "electricity": "🔌 Electricity Outages",
            "water": "🚰 Water Outages",
            "emergency": "🚨 Emergency Contacts",
            "main_menu": "🏠 Main Menu",
        },
        "tr": {
            "pharmacies": "💊 Nobetci Eczaneler",
            "electricity": "🔌 Elektrik Kesintileri",
            "water": "🚰 Su Kesintileri",
            "emergency": "🚨 Acil Hizmetler",
            "main_menu": "🏠 Ana Menu",
        },
    }.get(lang, {
        "pharmacies": "💊 Дежурные аптеки",
        "electricity": "🔌 Отключения электричества",
        "water": "🚰 Отключения воды",
        "emergency": "🚨 Экстренные службы",
        "main_menu": "🏠 Главное меню",
    })

    b = InlineKeyboardBuilder()
    b.button(text=labels["pharmacies"], callback_data=CITY_EVENTS_PHARMACIES_CB)
    b.button(text=labels["electricity"], callback_data=CITY_EVENTS_ELECTRICITY_CB)
    b.button(text=labels["water"], callback_data=CITY_EVENTS_WATER_CB)
    b.button(text=labels["emergency"], callback_data=CITY_EVENTS_EMERGENCY_CB)
    b.button(text=labels["main_menu"], callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()


def build_city_events_back_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    labels = {
        "ru": {"back": "⬅️ Назад", "main_menu": "🏠 Главное меню"},
        "en": {"back": "⬅️ Back", "main_menu": "🏠 Main Menu"},
        "tr": {"back": "⬅️ Geri", "main_menu": "🏠 Ana Menu"},
    }.get(lang, {"back": "⬅️ Назад", "main_menu": "🏠 Главное меню"})

    b = InlineKeyboardBuilder()
    b.button(text=labels["back"], callback_data=CITY_EVENTS_BACK_CB)
    b.button(text=labels["main_menu"], callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()
