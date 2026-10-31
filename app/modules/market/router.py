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


MARKET_DESCRIPTIONS = {
    "ru": (
        "🛍 AliMind MARKET — поиск недвижимости и вещей в Аланье\n\n"
        "Городской поисковый сервис AliMind City.\n\n"
        "🏠 Недвижимость\n"
        "AliMind SEARCH: квартиры, виллы и другие объекты для покупки или аренды в Аланье.\n\n"
        "🛒 Вещи и техника\n"
        "Будущий поиск объявлений о продаже мебели, бытовой техники и других вещей "
        "из Telegram-групп Аланьи. Раздел в разработке.\n\n"
        "👇 Выберите интересующий раздел."
    ),
    "en": (
        "🛍 AliMind MARKET — find property and second-hand goods in Alanya\n\n"
        "A city search service by AliMind City.\n\n"
        "🏠 Real estate\n"
        "AliMind SEARCH: apartments, villas and other properties to buy or rent in Alanya.\n\n"
        "🛒 Goods and electronics\n"
        "A future search for furniture, appliances and other items listed in Alanya "
        "Telegram groups. This section is under development.\n\n"
        "👇 Choose a section."
    ),
    "tr": (
        "🛍 AliMind MARKET — Alanya'da emlak ve ikinci el eşya arama\n\n"
        "AliMind City'nin şehir arama hizmeti.\n\n"
        "🏠 Gayrimenkul\n"
        "AliMind SEARCH: Alanya'da satılık veya kiralık daire, villa ve diğer gayrimenkuller.\n\n"
        "🛒 Eşya ve elektronik\n"
        "Alanya'daki Telegram gruplarında paylaşılan mobilya, beyaz eşya ve diğer "
        "satılık ürün ilanları için planlanan arama. Bu bölüm geliştirme aşamasındadır.\n\n"
        "👇 Bir bölüm seçin."
    ),
}


def market_keyboard(lang: str):
    estate, goods, back, *_ = LABELS.get(lang, LABELS["ru"])
    builder = InlineKeyboardBuilder()
    url = os.getenv("ALIMIND_SEARCH_URL", "https://alimindcity.com/search-ai/").strip()
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
    await callback.message.edit_text(MARKET_DESCRIPTIONS.get(lang, MARKET_DESCRIPTIONS["ru"]), reply_markup=market_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.in_({"market:goods", "market:search_unconfigured"}))
async def market_placeholder(callback: CallbackQuery) -> None:
    lang = language(callback)
    labels = LABELS.get(lang, LABELS["ru"])
    message = labels[4] if callback.data == "market:goods" else labels[5]
    await callback.message.edit_text(message, reply_markup=market_keyboard(lang))
    await callback.answer()
