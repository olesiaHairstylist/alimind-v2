from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.service import get_user_lang
from app.modules.directory.contracts.callbacks import build_directory_subcategory_cb
from app.modules.directory.contracts.categories import get_subcategory_title
from app.modules.directory.search_map import find_directory_target

router = Router()


def _is_search_query(text: str | None) -> bool:
    if not text:
        return False

    if text.startswith("/"):
        return False

    return find_directory_target(text) is not None


@router.message(F.text.func(_is_search_query))
async def directory_search_handler(message: Message) -> None:
    lang = get_user_lang(message.from_user.id) if message.from_user else "ru"
    target = find_directory_target(message.text or "")

    if not target:
        return

    category_id, subcategory_id = target
    subcategory_title = get_subcategory_title(subcategory_id, lang)

    b = InlineKeyboardBuilder()
    b.button(
        text=f"Открыть: {subcategory_title}",
        callback_data=build_directory_subcategory_cb(category_id, subcategory_id),
    )
    b.button(text="🏠 Главное меню", callback_data="main:menu")
    b.adjust(1)

    await message.answer(
        f"Нашёл подходящий раздел:\n\n{subcategory_title}",
        reply_markup=b.as_markup(),
    )