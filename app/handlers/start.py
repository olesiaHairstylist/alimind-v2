from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.keyboard import build_language_kb
from app.modules.core.language.service import get_user_lang
from app.modules.directory.handlers.object import send_directory_object_card
from app.modules.city_events.ui.handlers import send_pharmacies_by_district
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

router = Router()

TICKETS_PARTNER_URL = "YOUR_PARTNER_URL"


def render_main_menu_text(lang: str = "ru") -> str:
    text_map = {
        "ru": (
            "Актуальная информация по городу\n\n"
            "⚡ Отключения\n"
            "🏥 Дежурные аптеки\n\n"
            "🔄 Обновлено: 16:12\n\n"
            "Что вам нужно сейчас?\n"
            "Выберите — покажу быстро 👇"
        ),
        "en": (
            "Current city information\n\n"
            "⚡ Outages\n"
            "🏥 Duty pharmacies\n\n"
            "🔄 Updated: 16:12\n\n"
            "What do you need now?\n"
            "Choose — I’ll show it quickly 👇"
        ),
        "tr": (
            "Güncel şehir bilgileri\n\n"
            "⚡ Kesintiler\n"
            "🏥 Nöbetçi eczaneler\n\n"
            "🔄 Güncellendi: 16:12\n\n"
            "Şimdi neye ihtiyacınız var?\n"
            "Seçin — hızlıca göstereyim 👇"
        ),
    }
    return text_map.get(lang, text_map["ru"])


def build_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    all_labels = {
        "ru": {
            "city": "⚡ Город сейчас",
            "services": "🛠 Услуги",
            "sport": " Спорт",
            "tickets": "✈️ Билеты",
            "phrasebook": "💬 Разговорник",
            "currency": "💱 Валюта",
            "sea": "🌊 Море",
            "news": "📰 Новости Аланьи ",
            "rent": "🏠 Недвижимость Аланьи",
            "pharmacies": "💊 Дежурные аптеки",
            "alanya_online": "📹 Алания онлайн",
            # ru
            "esim": "📱 eSIM −15%",


        },
        "en": {
            "city": "⚡ City now",
            "services": "🛠 Services",
            "sport": " Sport",
            "rent": "🏠 Housing",
            "tickets": "✈️ Flights",
            "phrasebook": "💬 Phrasebook",
            "currency": "💱 Currency",
            "sea": "🌊 Sea",
            "news": "📰 Новости Аланьи ",
            "pharmacies": "💊 Duty Pharmacies",
            "alanya_online": "📹 Alanya Live",
            "esim": "📱 eSIM −15%",


        },
        "tr": {
            "city": "⚡ Şehir şimdi",
            "services": "🛠 Hizmetler",
            "sport": " Spor",
            "rent": "🏠 Konut",
            "tickets": "✈️ Biletler",
            "phrasebook": "💬 Konuşma",
            "currency": "💱 Döviz",
            "sea": "🌊 Deniz",
            "news": "📰 Новости Аланьи ",
            "pharmacies": "💊 Nöbetçi Eczaneler",
            "alanya_online": "📹 Alanya Canlı",
            "esim": "📱 eSIM −15%",


        },
    }

    labels = all_labels.get(lang, all_labels["ru"])

    b = InlineKeyboardBuilder()

    b.button(text=labels["city"], callback_data="city_events:menu")
    b.button(text=labels["services"], callback_data="directory:menu")
    b.button(
        text=labels["sport"],
        callback_data="directory:category:sport"
    )

    b.button(
        text=labels["rent"],
        url="https://t.me/alanya_rent07/16",
    )
    b.button(text=labels["tickets"], url="https://aviasales.tpm.li/zQsb4TXR")
    b.button(text=labels["phrasebook"], callback_data="phrasebook:menu")
    b.button(text=labels["currency"], callback_data="currency:menu")
    b.button(text="🧾  ВНЖ", callback_data="rescalc:start")
    b.button(text=labels["sea"], callback_data="sea_status:open")
    b.button(
        text=labels["esim"],
        callback_data="partner:yesim:open",
    )

    b.button(text=labels["news"], url="https://t.me/alania_life07")

    b.button(
        text=labels["pharmacies"],
        callback_data="city_events:pharmacies",
    )
    b.adjust(1, 2, 2, 3, 1, 1, 1, 1)
    return b.as_markup()


def _extract_start_object_id(message: Message) -> str | None:
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        return None

    payload = parts[1].strip()
    if not payload.startswith("obj_"):
        return None

    object_id = payload.removeprefix("obj_").strip()
    return object_id or None


def _extract_start_pharmacy_code(message: Message) -> str | None:
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1].strip()
    if not payload.startswith("pharmacy_"):
        return None
    code = payload.removeprefix("pharmacy_").strip()
    return code or None


def _directory_empty_text(lang: str) -> str:
    return {
        "ru": "Объект не найден",
        "en": "Object not found",
        "tr": "Nesne bulunamadı",
    }.get(lang, "Объект не найден")


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = message.from_user
    user_lang = get_user_lang(user.id) if user else None
    object_id = _extract_start_object_id(message)
    pharmacy_code = _extract_start_pharmacy_code(message)

    if not user_lang:
        if object_id:
            await state.update_data(pending_start_object_id=object_id)
        elif pharmacy_code:
            await state.update_data(pending_start_pharmacy_code=pharmacy_code)
        await message.answer(
            "Выберите язык / Select language / Dil seçin",
            reply_markup=build_language_kb(),
        )
        return

    if object_id:
        opened = await send_directory_object_card(message, object_id, user_lang)
        if opened:
            return

        await message.answer(_directory_empty_text(user_lang))

    if pharmacy_code:
        await send_pharmacies_by_district(message, pharmacy_code, user_lang)
        return

    await message.answer(
        render_main_menu_text(user_lang),
        reply_markup=build_main_menu(user_lang),
    )


@router.callback_query(lambda c: c.data == "main:menu")
async def open_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user = callback.from_user
    user_lang = get_user_lang(user.id) if user else "ru"
    text = render_main_menu_text(user_lang or "ru")
    reply_markup = build_main_menu(user_lang or "ru")

    if (
            callback.message.photo
            or callback.message.video
    ):
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        await callback.message.answer(
            text,
            reply_markup=reply_markup,
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
        )

@router.callback_query(lambda c: c.data == "partner:yesim:open")
async def open_yesim_offer(callback: CallbackQuery) -> None:
    user = callback.from_user
    user_lang = get_user_lang(user.id) if user else "ru"

    text_map = {
        "ru": (
            "📱 eSIM для путешествий\n\n"
            "Мобильный интернет без физической SIM-карты.\n"
            "Работает во многих странах мира.\n\n"
            "🎁 Скидка 15% на первую покупку Yesim\n"
            "Промокод: ALIMIND15"
        ),
        "en": (
            "📱 eSIM for travel\n\n"
            "Mobile internet without a physical SIM card.\n"
            "Available in many countries worldwide.\n\n"
            "🎁 15% off your first Yesim purchase\n"
            "Promo code: ALIMIND15"
        ),
        "tr": (
            "📱 Seyahat için eSIM\n\n"
            "Fiziksel SIM kart olmadan mobil internet.\n"
            "Dünyanın birçok ülkesinde kullanılabilir.\n\n"
            "🎁 İlk Yesim alışverişinde %15 indirim\n"
            "Promosyon kodu: ALIMIND15"
        ),
    }

    b = InlineKeyboardBuilder()

    b.button(
        text={
            "ru": "🌍 Выбрать eSIM",
            "en": "🌍 Choose eSIM",
            "tr": "🌍 eSIM seç",
        }.get(user_lang or "ru", "🌍 Выбрать eSIM"),
        url="https://yesim.app/?partner_id=5253",
    )

    b.button(
        text={
            "ru": "⬅️ Назад",
            "en": "⬅️ Back",
            "tr": "⬅️ Geri",
        }.get(user_lang or "ru", "⬅️ Назад"),
        callback_data="main:menu",
    )

    b.adjust(1)

    await callback.message.edit_text(
        text_map.get(user_lang or "ru", text_map["ru"]),
        reply_markup=b.as_markup(),
    )

    await callback.answer()
