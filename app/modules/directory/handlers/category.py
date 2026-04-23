from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.modules.core.language.service import get_user_lang
from app.modules.directory.contracts.callbacks import (
    is_directory_category_cb,
    parse_directory_category_cb,
)
from app.modules.directory.contracts.categories import get_category_title
from app.modules.directory.render.keyboard_render import build_directory_subcategories_kb
from app.modules.directory.services.loader import load_subcategories

router = Router()


def _texts(lang: str) -> dict[str, str]:
    return {
        "ru": {
            "error": "Ошибка категории",
            "empty": "Подкатегории не найдены",
            "choose": "Выберите подкатегорию:",
        },
        "en": {
            "error": "Category error",
            "empty": "No subcategories found",
            "choose": "Choose a subcategory:",
        },
        "tr": {
            "error": "Kategori hatası",
            "empty": "Alt kategoriler bulunamadı",
            "choose": "Bir alt kategori seçin:",
        },
    }.get(lang, {
        "error": "Ошибка категории",
        "empty": "Подкатегории не найдены",
        "choose": "Выберите подкатегорию:",
    })


@router.callback_query(F.data.func(is_directory_category_cb))
async def open_directory_category(callback: CallbackQuery) -> None:
    data = callback.data or ""
    category_id = parse_directory_category_cb(data)
    lang = get_user_lang(callback.from_user.id) or "ru"
    texts = _texts(lang)

    if not category_id:
        await callback.answer(texts["error"], show_alert=False)
        return

    subcategories = load_subcategories(category_id)

    category_title = get_category_title(category_id, lang)

    if not subcategories:
        await callback.answer(texts["empty"], show_alert=False)
        return

    await callback.message.edit_text(
        f"📂 {category_title}\n\n{texts['choose']}",
        reply_markup=build_directory_subcategories_kb(category_id, subcategories, lang),
    )
    await callback.answer()
