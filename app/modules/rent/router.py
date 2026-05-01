from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def build_rent_stub_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Назад в меню", callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()


@router.callback_query(F.data == "rent:entry")
async def rent_entry_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "🏠 Жильё в Алании\n\n"
        "Раздел скоро будет работать.\n\n"
        "Здесь появится помощник по аренде: районы, бюджет, чек-лист перед оплатой и риски.",
        reply_markup=build_rent_stub_kb(),
    )
    await callback.answer()