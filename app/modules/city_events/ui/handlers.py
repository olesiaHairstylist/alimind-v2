from __future__ import annotations

from pathlib import Path
from typing import Any

from aiogram.types import CallbackQuery

from app.modules.city_events.contracts.categories import CityEventCategory
from app.modules.city_events.render.keyboard_render import (
    build_city_events_back_kb,
    build_city_events_menu_kb,
)
from app.modules.city_events.render.renderers import (
    render_category_payload,
    render_emergency,
    render_pharmacies,
)
from app.modules.city_events.render.electricity_render import render_electricity
from app.modules.city_events.storage.public_reader import read_public_file
from app.modules.city_events.storage.reader import read_payload
from app.modules.core.language.service import get_user_lang

APP_DIR = Path(__file__).resolve().parents[3]

PHARMACIES_PUBLIC_FILE = (
    APP_DIR
    / "data"
    / "public"
    / "city_events"
    / "duty_pharmacies_today.json"
)
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "city_events"

ELECTRICITY_PUBLIC_FILE = (
    APP_DIR
    / "data"
    / "public"
    / "city_events"
    / "electricity_outages_today.json"
)
EMERGENCY_PUBLIC_FILE = (
    APP_DIR
    / "data"
    / "public"
    / "city_events"
    / "emergency_contacts.json"
)


def _get_lang(callback: CallbackQuery) -> str:
    return get_user_lang(callback.from_user.id) or "ru"


def _menu_text(lang: str) -> str:
    return {
        "ru": "События города\n\nВыберите раздел:",
        "en": "City Events\n\nChoose a section:",
        "tr": "Şehir Etkinlikleri\n\nBir bölüm seçin:",
    }.get(lang, "События города\n\nВыберите раздел:")


async def open_city_events_menu(callback: CallbackQuery) -> None:
    lang = _get_lang(callback)

    await callback.message.edit_text(
        _menu_text(lang),
        reply_markup=build_city_events_menu_kb(lang),
    )
    await callback.answer()


async def open_pharmacies(callback: CallbackQuery) -> None:
    lang = _get_lang(callback)
    data = read_public_file(PHARMACIES_PUBLIC_FILE)
    text = render_pharmacies(data, lang=lang)

    await callback.message.edit_text(
        text,
        parse_mode=None,
        reply_markup=build_city_events_back_kb(lang),
    )


async def open_electricity(callback: CallbackQuery) -> None:
    lang = _get_lang(callback)
    data = read_public_file(ELECTRICITY_PUBLIC_FILE)
    text = render_electricity(data, lang=lang)

    await callback.message.edit_text(
        text,
        parse_mode=None,
        reply_markup=build_city_events_back_kb(lang),
    )


async def open_water(callback: CallbackQuery) -> None:
    await _open_category(callback, CityEventCategory.WATER)


async def open_emergency(callback: CallbackQuery) -> None:
    lang = _get_lang(callback)
    data = read_public_file(EMERGENCY_PUBLIC_FILE)
    text = render_emergency(data, lang=lang)

    await callback.message.edit_text(
        text,
        parse_mode=None,
        reply_markup=build_city_events_back_kb(lang),
    )


async def _open_category(callback: CallbackQuery, category: CityEventCategory) -> None:
    lang = _get_lang(callback)
    payload = read_payload(DATA_DIR, category)

    if payload is None:
        no_data_text = {
            "ru": "Данные пока недоступны.",
            "en": "Data is temporarily unavailable.",
            "tr": "Veri simdilik kullanilamiyor.",
        }.get(lang, "Данные пока недоступны.")
        await callback.message.edit_text(
            no_data_text,
            reply_markup=build_city_events_back_kb(lang),
        )
        await callback.answer()
        return

    items = payload.get("items", [])
    if not isinstance(items, list):
        items = []

    max_items = 15
    payload_for_render: dict[str, Any] = {
        "category": payload.get("category", category.value),
        "updated_at": payload.get("updated_at", ""),
        "items": items[:max_items],
    }

    text = render_category_payload(category.value, payload_for_render, lang=lang)

    if len(items) > max_items:
        limit_note = {
            "ru": f"\n\nПоказаны первые {max_items} записей.",
            "en": f"\n\nShowing first {max_items} records.",
            "tr": f"\n\nIlk {max_items} kayit gosteriliyor.",
        }.get(lang, f"\n\nПоказаны первые {max_items} записей.")
        text += limit_note

    await callback.message.edit_text(
        text,
        reply_markup=build_city_events_back_kb(lang),
    )
    await callback.answer()
