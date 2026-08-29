from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aiogram.types import CallbackQuery, Message
from urllib.parse import quote_plus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.modules.city_events.ui.callbacks import CITY_EVENTS_BACK_CB
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
from app.modules.city_events.services.pharmacy_districts import (
    PHARMACY_DISTRICTS,
    district_label,
    filter_pharmacies,
    item_district_code,
)

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
def build_pharmacies_action_kb(items: list[dict[str, Any]], lang: str):
    b = InlineKeyboardBuilder()

    labels = {
        "ru": {"back": "⬅️ Назад"},
        "en": {"back": "⬅️ Back"},
        "tr": {"back": "⬅️ Geri"},
    }.get(lang, {"back": "⬅️ Назад"})

    for idx, item in enumerate(items, start=1):
        title = item.get("title") or item.get("name") or f"Аптека {idx}"
        address = item.get("address", "")
        query = f"{title} {address} Alanya"
        url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"

        b.button(text=f"📍 {idx}. {title[:28]}", url=url)

    b.button(text=labels["back"], callback_data=CITY_EVENTS_BACK_CB)
    b.adjust(1)
    return b.as_markup()


def build_pharmacy_districts_kb(lang: str, *, show_all: bool = True):
    b = InlineKeyboardBuilder()
    for code, district in PHARMACY_DISTRICTS.items():
        b.button(
            text=str(district["label"]),
            callback_data=f"pharmacy:district:{code}",
        )

    if show_all:
        all_label = {
            "ru": "Все дежурные аптеки",
            "en": "All duty pharmacies",
            "tr": "Tüm nöbetçi eczaneler",
        }.get(lang, "Все дежурные аптеки")
        b.button(text=f"💊 {all_label}", callback_data="pharmacy:district:all")

    main_label = {
        "ru": "Главное меню",
        "en": "Main menu",
        "tr": "Ana menü",
    }.get(lang, "Главное меню")
    b.button(text=f"🏠 {main_label}", callback_data="main:menu")
    b.adjust(2, 2, 2, 2, 2, 1, 1)
    return b.as_markup()


def _pharmacy_card_text(item: dict[str, Any], district: str, lang: str) -> str:
    title = str(item.get("title") or item.get("name") or "").strip()
    address = str(item.get("address") or "").strip()
    # Telegram treats `CAD.NO:129` as a URL because `.no` is a real domain.
    address = re.sub(
        r"\bCAD\.\s*NO\s*:?\s*",
        "CAD. NO ",
        address,
        flags=re.IGNORECASE,
    )
    phone = str(item.get("phone") or "").strip()
    heading = {
        "ru": f"📍 Дежурная аптека в районе {district}",
        "en": f"📍 Duty pharmacy in {district}",
        "tr": f"📍 {district} bölgesinde nöbetçi eczane",
    }.get(lang, f"📍 Дежурная аптека в районе {district}")
    lines = [heading, "", title]
    if address:
        lines.extend(("", f"🏠 {address}"))
    if phone:
        lines.extend(("", f"☎️ {phone}"))
    return "\n".join(lines)


def _pharmacy_card_kb(item: dict[str, Any], district: str, lang: str):
    b = InlineKeyboardBuilder()
    title = str(item.get("title") or item.get("name") or "Аптека").strip()
    address = str(item.get("address") or "").strip()
    query = quote_plus(f"{title} {address} Alanya")
    route_label = {
        "ru": f"📍 Маршрут — {title}",
        "en": f"📍 Route — {title}",
        "tr": f"📍 Yol tarifi — {title}",
    }.get(lang, f"📍 Маршрут — {title}")
    b.button(
        text=route_label[:64],
        url=f"https://www.google.com/maps/search/?api=1&query={query}",
    )
    b.adjust(1)
    return b.as_markup()


async def send_pharmacies_by_district(
    message: Message, district_code: str, lang: str
) -> bool:
    if district_code != "all" and district_code not in PHARMACY_DISTRICTS:
        text = {
            "ru": "Район не найден. Выберите район:",
            "en": "Area not found. Choose an area:",
            "tr": "Bölge bulunamadı. Bir bölge seçin:",
        }.get(lang, "Район не найден. Выберите район:")
        await message.answer(text, reply_markup=build_pharmacy_districts_kb(lang))
        return False

    data = read_public_file(PHARMACIES_PUBLIC_FILE)
    raw_items = data.get("items") or []
    items = [item for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []
    selected = filter_pharmacies(items, district_code)
    label = "Alanya" if district_code == "all" else (district_label(district_code) or district_code)

    if not selected:
        text = {
            "ru": f"Сегодня в районе {label} дежурная аптека не найдена.",
            "en": f"No duty pharmacy was found in {label} today.",
            "tr": f"Bugün {label} bölgesinde nöbetçi eczane bulunamadı.",
        }.get(lang, f"Сегодня в районе {label} дежурная аптека не найдена.")
        await message.answer(text, reply_markup=build_pharmacy_districts_kb(lang))
        return True

    for item in selected:
        item_code = district_code if district_code != "all" else None
        if item_code is None:
            item_code = item_district_code(item)
        item_label = district_label(item_code or "") or label
        await message.answer(
            _pharmacy_card_text(item, item_label, lang),
            reply_markup=_pharmacy_card_kb(item, item_label, lang),
        )

    if district_code == "all":
        follow_up = {
            "ru": "Выберите район или вернитесь в главное меню:",
            "en": "Choose an area or return to the main menu:",
            "tr": "Bir bölge seçin veya ana menüye dönün:",
        }.get(lang, "Выберите район или вернитесь в главное меню:")
    else:
        follow_up = {
            "ru": "Показать другие аптеки или выбрать другой район:",
            "en": "Show other pharmacies or choose another area:",
            "tr": "Diğer eczaneleri gösterin veya başka bir bölge seçin:",
        }.get(lang, "Показать другие аптеки или выбрать другой район:")
    await message.answer(
        follow_up,
        reply_markup=build_pharmacy_districts_kb(
            lang,
            show_all=district_code != "all",
        ),
    )
    return True


async def open_pharmacy_district(callback: CallbackQuery) -> None:
    district_code = (callback.data or "").rsplit(":", 1)[-1]
    lang = _get_lang(callback)
    await send_pharmacies_by_district(callback.message, district_code, lang)
    await callback.answer()

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
    print("ELECTRICITY_PUBLIC_FILE:", ELECTRICITY_PUBLIC_FILE)
    print("ELECTRICITY_ITEMS:", len(data.get("items", [])))
    print("ELECTRICITY_DATA:", data)
    text = render_pharmacies(data, lang=lang)

    items = data.get("items") or []
    if not isinstance(items, list):
        items = []

    await callback.message.edit_text(
        text,
        parse_mode=None,
        reply_markup=build_pharmacies_action_kb(items, lang),
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

    items = data.get("items") or []
    if not isinstance(items, list):
        items = []

    await callback.message.edit_text(
        text,
        parse_mode=None,
        reply_markup=build_pharmacies_action_kb(items, lang),
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
