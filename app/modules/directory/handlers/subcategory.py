from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.modules.core.language.service import get_user_lang
from app.modules.directory.contracts.callbacks import (
    is_directory_subcategory_cb,
    parse_directory_subcategory_cb,
)

from app.modules.directory.render.keyboard_render import build_directory_objects_kb
from app.modules.directory.services.loader import load_objects_by_subcategory
from app.modules.directory.contracts.categories import (
    get_category_title,
    get_subcategory_title,
)
router = Router()


def _texts(lang: str) -> dict[str, str]:
    return {
        "ru": {
            "error": "Ошибка подкатегории",
            "empty": "Услуги не найдены",
            "choose": "Доступные услуги:",
        },
        "en": {
            "error": "Subcategory error",
            "empty": "No services found",
            "choose": "Available services:",
        },
        "tr": {
            "error": "Alt kategori hatası",
            "empty": "Hizmet bulunamadı",
            "choose": "Mevcut hizmetler:",
        },
    }.get(lang, {
        "error": "Ошибка подкатегории",
        "empty": "Услуги не найдены",
        "choose": "Доступные услуги:",
    })


@router.callback_query(F.data.func(is_directory_subcategory_cb))
async def open_directory_subcategory(callback: CallbackQuery) -> None:
    data = callback.data or ""
    parsed = parse_directory_subcategory_cb(data)
    lang = get_user_lang(callback.from_user.id) or "ru"
    texts = _texts(lang)

    if not parsed:
        await callback.answer(texts["error"], show_alert=False)
        return

    category_id, subcategory_id = parsed
    objects = load_objects_by_subcategory(subcategory_id)

    category_title = get_category_title(category_id, lang)
    subcategory_title = get_subcategory_title(subcategory_id, lang)

    if not objects:
        await callback.answer(texts["empty"], show_alert=False)
        return

    screen_text = f"📂 {category_title} → {subcategory_title}\n\n{texts['choose']}"

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            screen_text,
            reply_markup=build_directory_objects_kb(objects, lang),
        )
    else:
        await callback.message.edit_text(
            screen_text,
            reply_markup=build_directory_objects_kb(objects, lang),
        )

    await callback.answer()