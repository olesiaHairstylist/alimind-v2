from __future__ import annotations

from app.core.text import get_text
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.directory.contracts.callbacks import (
    DIRECTORY_MENU_CB,
    build_directory_category_cb,
    build_directory_subcategory_cb,
    build_directory_open_cb,
)
from app.modules.directory.contracts.categories import (
    CATEGORY_ORDER,
    get_category_title,
    get_subcategory_title,
)
def _nav_texts(lang: str) -> dict[str, str]:
    return {
        "ru": {
            "services": "⬅️ К услугам",
            "back": "⬅️ Назад",
            "main_menu": "🏠 Главное меню",
            "untitled": "Без названия",
        },
        "en": {
            "services": "⬅️ Back to Services",
            "back": "⬅️ Back",
            "main_menu": "🏠 Main Menu",
            "untitled": "Untitled",
        },
        "tr": {
            "services": "⬅️ Hizmetlere Dön",
            "back": "⬅️ Geri",
            "main_menu": "🏠 Ana Menü",
            "untitled": "Adsız",
        },
    }.get(lang, {
        "services": "⬅️ К услугам",
        "back": "⬅️ Назад",
        "main_menu": "🏠 Главное меню",
        "untitled": "Без названия",
    })


def build_directory_categories_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    texts = _nav_texts(lang)

    for category_id in CATEGORY_ORDER:
        b.button(
            text=get_category_title(category_id, lang),
            callback_data=build_directory_category_cb(category_id),
        )


    b.button(text=texts["main_menu"], callback_data="main:menu")
    b.adjust(1)

    return b.as_markup()


def build_directory_subcategories_kb(
    category_id: str,
    subcategories: list[str],
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    texts = _nav_texts(lang)

    for subcategory_id in subcategories:
        b.button(
            text=get_subcategory_title(subcategory_id, lang),
            callback_data=build_directory_subcategory_cb(category_id, subcategory_id),
        )


    b.button(text=texts["main_menu"], callback_data="main:menu")
    b.adjust(*([1] * len(subcategories)), 2)

    return b.as_markup()


def build_directory_objects_kb(objects: list[dict], lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    texts = _nav_texts(lang)

    for obj in objects:
        b.button(
            text=get_text(obj.get("title"), lang) or texts["untitled"],
            callback_data=build_directory_open_cb(obj["id"]),
        )

    b.button(text=texts["services"], callback_data=DIRECTORY_MENU_CB)
    b.button(text=texts["main_menu"], callback_data="main:menu")
    b.adjust(1)

    return b.as_markup()


def build_directory_object_back_kb(
    category_id: str,
    subcategory_id: str,
    lang: str = "ru",
    object_id: str | None = None,
    has_maps: bool = False,
    instagram_url: str | None = None,
) -> InlineKeyboardMarkup:
    print("DEBUG MAP BUTTON:", has_maps, object_id)
    b = InlineKeyboardBuilder()
    texts = _nav_texts(lang)

    # 📍 КНОПКА КАРТЫ (первая строка)
    if has_maps and object_id:
        b.button(
            text="📍 Как добраться",
            callback_data=f"maps:open:{object_id}",
        )
    if instagram_url:
        b.button(
            text="📷 Instagram",
            url=instagram_url,
        )

    # 🔙 Назад
    b.button(
        text=texts["back"],
        callback_data=build_directory_subcategory_cb(category_id, subcategory_id),
    )

    # 🏠 Главное меню
    b.button(
        text=texts["main_menu"],
        callback_data="main:menu",
    )

    b.adjust(1)

    return b.as_markup()
