from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.city_events.contracts.messages import (
    BACK_BUTTON,
    MAIN_MENU_BUTTON,
    TITLE_ELECTRICITY,
    TITLE_EMERGENCY,
    TITLE_PHARMACIES,
    TITLE_WATER,
)
from app.modules.city_events.ui.callbacks import (
    CITY_EVENTS_BACK_CB,
    CITY_EVENTS_ELECTRICITY_CB,
    CITY_EVENTS_EMERGENCY_CB,
    CITY_EVENTS_MAIN_MENU_CB,
    CITY_EVENTS_PHARMACIES_CB,
    CITY_EVENTS_WATER_CB,
)


def build_city_events_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=TITLE_PHARMACIES, callback_data=CITY_EVENTS_PHARMACIES_CB)
    b.button(text=TITLE_ELECTRICITY, callback_data=CITY_EVENTS_ELECTRICITY_CB)
    b.button(text=TITLE_WATER, callback_data=CITY_EVENTS_WATER_CB)
    b.button(text=TITLE_EMERGENCY, callback_data=CITY_EVENTS_EMERGENCY_CB)
    b.button(text=MAIN_MENU_BUTTON, callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()


def build_city_events_back_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=BACK_BUTTON, callback_data=CITY_EVENTS_BACK_CB)
    b.button(text=MAIN_MENU_BUTTON, callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()