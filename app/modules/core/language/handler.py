from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.start import build_main_menu, render_main_menu_text
from app.modules.core.language.keyboard import build_language_kb
from app.modules.core.language.service import set_user_lang
from app.modules.directory.handlers.object import send_directory_object_card

router = Router()


def _language_prompt_text() -> str:
    return "Выберите язык / Select language / Dil secin"


@router.message(Command("language"))
async def language_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        _language_prompt_text(),
        reply_markup=build_language_kb(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lang = (callback.data or "").split(":", 1)[1]
    data = await state.get_data()
    pending_object_id = str(data.get("pending_start_object_id", "")).strip()
    set_user_lang(callback.from_user.id, lang)
    await state.clear()

    if pending_object_id:
        try:
            await callback.message.delete()
        except Exception:
            pass

        opened = await send_directory_object_card(callback.message, pending_object_id, lang)
        if opened:
            await callback.answer()
            return

        await callback.message.answer({
            "ru": "Объект не найден",
            "en": "Object not found",
            "tr": "Nesne bulunamadı",
        }.get(lang, "Объект не найден"))
        await callback.message.answer(
            render_main_menu_text(lang),
            reply_markup=build_main_menu(lang),
        )
        await callback.answer()
        return

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            render_main_menu_text(lang),
            reply_markup=build_main_menu(lang),
        )
    else:
        await callback.message.edit_text(
            render_main_menu_text(lang),
            reply_markup=build_main_menu(lang),
        )

    await callback.answer()
