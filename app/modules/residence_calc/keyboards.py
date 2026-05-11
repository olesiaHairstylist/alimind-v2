from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.residence_calc.data import COUNTRIES


def build_country_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    for code, country in COUNTRIES.items():
        b.button(
            text=country["name"],
            callback_data=f"rescalc:country:{code}",
        )
    b.button(text="⬅️ Назад", callback_data="rescalc:back:menu")
    b.adjust(2)
    return b.as_markup()


def build_application_type_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    b.button(text="Первичная подача", callback_data="rescalc:type:first")
    b.button(text="Продление", callback_data="rescalc:type:renew")
    b.button(text="⬅️ Назад", callback_data="rescalc:back:country")
    b.adjust(1)
    return b.as_markup()