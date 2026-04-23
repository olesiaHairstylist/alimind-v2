from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.keyboard import build_language_kb
from app.modules.core.language.service import get_user_lang
from app.modules.directory.handlers.object import send_directory_object_card
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

router = Router()

TICKETS_PARTNER_URL = "YOUR_PARTNER_URL"


def render_main_menu_text(lang: str = "ru") -> str:
    text_map = {
        "ru": "Добро пожаловать в AliMind",
        "en": "Welcome to AliMind",
        "tr": "AliMind'e hoş geldiniz",
    }
    return text_map.get(lang, text_map["ru"])

def build_main_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    labels = {
        "ru": {
            "sea_status": "🌊 Море сейчас",
            "city_events": "🏙 События города",
            "directory": "🛠 Услуги",
            "tickets_entry": "✈️ Поиск билетов",
            "phrasebook": "🗣 Разговорник",
            "info": "ℹ️ Информация",
            "website": "🌐 Сайт AliMind",
        },
        "en": {
            "sea_status": "🌊 Sea now",
            "city_events": "🏙 City Events",
            "directory": "🛠 Services",
            "tickets_entry": "✈️ Ticket search",
            "phrasebook": "🗣 Phrasebook",
            "info": "ℹ️ Information",
            "website": "🌐 AliMind Website",
        },
        "tr": {
            "sea_status": "🌊 Deniz şimdi",
            "city_events": "🏙 Şehir Etkinlikleri",
            "directory": "🛠 Hizmetler",
            "tickets_entry": "✈️ Bilet ara",
            "phrasebook": "🗣 Konuşma kalıpları",
            "info": "ℹ️ Bilgi",
            "website": "🌐 AliMind Sitesi",
        },
    }.get(
        lang,
        {
            "sea_status": "🌊 Море сейчас",
            "city_events": "🏙 События города",
            "directory": "🛠 Услуги",
            "tickets_entry": "✈️ Поиск билетов",
            "phrasebook": "🗣 Разговорник",
            "info": "ℹ️ Информация",
            "website": "🌐 Сайт AliMind",
        },
    )

    b = InlineKeyboardBuilder()
    b.button(text=labels["sea_status"], callback_data="sea_status:open")
    b.button(text=labels["city_events"], callback_data="city_events:menu")
    b.button(text=labels["directory"], callback_data="directory:menu")
    b.button(text=labels["tickets_entry"], url="https://aviasales.tpm.li/zQsb4TXR")
    b.button(text=labels["phrasebook"], callback_data="phrasebook:menu")
    b.button(text=labels["info"], callback_data="main:info")
    b.button(text=labels["website"], url="https://alimindcity.com/")
    b.adjust(1)
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

    if not user_lang:
        if object_id:
            await state.update_data(pending_start_object_id=object_id)
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

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text,
            reply_markup=reply_markup,
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
        )

    await callback.answer()