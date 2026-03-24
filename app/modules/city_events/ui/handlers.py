from __future__ import annotations

from pathlib import Path

from aiogram.types import CallbackQuery

from app.modules.city_events.contracts.categories import CityEventCategory
from app.modules.city_events.render.keyboard_render import (
    build_city_events_back_kb,
    build_city_events_menu_kb,
)
from app.modules.city_events.render.text_render import render_category_payload
from app.modules.city_events.storage.reader import read_payload


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "city_events"


async def open_city_events_menu(callback: CallbackQuery) -> None:
    text = (
        "События города\n\n"
        "Выберите категорию:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=build_city_events_menu_kb(),
    )
    await callback.answer()


async def open_pharmacies(callback: CallbackQuery) -> None:
    await _open_category(callback, CityEventCategory.PHARMACIES)


async def open_electricity(callback: CallbackQuery) -> None:
    await _open_category(callback, CityEventCategory.ELECTRICITY)


async def open_water(callback: CallbackQuery) -> None:
    await _open_category(callback, CityEventCategory.WATER)


async def open_emergency(callback: CallbackQuery) -> None:
    await _open_category(callback, CityEventCategory.EMERGENCY)


async def _open_category(callback: CallbackQuery, category: CityEventCategory) -> None:
    payload = read_payload(DATA_DIR, category)

    if payload is None:
        await callback.message.edit_text(
            "Данные пока недоступны.",
            reply_markup=build_city_events_back_kb(),
        )
        await callback.answer()
        return

    max_items = 15
    original_items = payload.items
    payload.items = payload.items[:max_items]

    text = render_category_payload(category, payload)

    payload.items = original_items

    if len(original_items) > max_items:
        text += f"\n\nПоказаны первые {max_items} записей."

    await callback.message.edit_text(
        text,
        reply_markup=build_city_events_back_kb(),
    )
    await callback.answer()