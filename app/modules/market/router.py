from __future__ import annotations

import os

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.service import get_user_lang

router = Router()

LABELS = {
    "ru": ("🏠 Недвижимость", "🛒 Вещи и техника", "↩️ Назад", "🛍 AliMind MARKET", "Раздел готовится", "Ссылка на SEARCH пока не настроена"),
    "en": ("🏠 Real estate", "🛒 Goods and electronics", "↩️ Back", "🛍 AliMind MARKET", "Coming soon", "SEARCH link is not configured yet"),
    "tr": ("🏠 Gayrimenkul", "🛒 Eşya ve elektronik", "↩️ Geri", "🛍 AliMind MARKET", "Bölüm hazırlanıyor", "SEARCH bağlantısı henüz ayarlanmadı"),
}


def market_keyboard(lang: str):
    estate, goods, back, *_ = LABELS.get(lang, LABELS["ru"])
    builder = InlineKeyboardBuilder()
    url = os.getenv("ALIMIND_SEARCH_URL", "").strip()
    if url.startswith(("https://", "http://")):
        builder.button(text=estate, url=url)
    else:
        builder.button(text=estate, callback_data="market:search_unconfigured")
    builder.button(text=goods, callback_data="market:goods")
    builder.button(text=back, callback_data="main:menu")
    builder.adjust(1)
    return builder.as_markup()


def language(callback: CallbackQuery) -> str:
    return get_user_lang(callback.from_user.id) or "ru"


@router.callback_query(F.data == "market:menu")
async def open_market(callback: CallbackQuery) -> None:
    lang = language(callback)
    await callback.message.edit_text(LABELS.get(lang, LABELS["ru"])[3], reply_markup=market_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.in_({"market:goods", "market:search_unconfigured"}))
async def market_placeholder(callback: CallbackQuery) -> None:
    lang = language(callback)
    labels = LABELS.get(lang, LABELS["ru"])
    message = labels[4] if callback.data == "market:goods" else labels[5]
    await callback.message.edit_text(message, reply_markup=market_keyboard(lang))
    await callback.answer()
