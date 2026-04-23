from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.modules.core.language.service import get_user_lang
from app.modules.directory.contracts.callbacks import DIRECTORY_MENU_CB
from app.modules.directory.render.keyboard_render import build_directory_categories_kb

router = Router()


@router.callback_query(F.data == DIRECTORY_MENU_CB)
async def open_directory_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    lang = get_user_lang(callback.from_user.id) or "ru"

    text = {
        "ru": "Выберите категорию:",
        "en": "Choose a category:",
        "tr": "Kategori seçin:",
    }.get(lang, "Выберите категорию:")

    kb = build_directory_categories_kb(lang)

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()