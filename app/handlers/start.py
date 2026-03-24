from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.city_events.ui.handlers import open_city_events_menu
from app.modules.core.language.keyboard import build_language_kb

router = Router()


def build_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🏙 События города", callback_data="main:city_events")
    kb.button(text="🛠 Услуги", callback_data="main:directory")
    kb.button(text="ℹ️ Информация", callback_data="main:info")
    kb.adjust(1)
    return kb.as_markup()


async def show_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Добро пожаловать в AliMind",
        reply_markup=build_main_menu()
    )
    await callback.answer()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Выберите язык / Select language",
        reply_markup=build_language_kb()
    )


@router.callback_query(lambda c: c.data in {"main:city_events", "main:info", "main:menu"})
async def main_menu_router(callback: CallbackQuery):
    data = callback.data

    if data == "main:city_events":
        await open_city_events_menu(callback)

    elif data == "main:info":
        await callback.message.edit_text(
            "Раздел информации (в разработке)",
            reply_markup=build_main_menu()
        )
        await callback.answer()

    elif data == "main:menu":
        await show_main_menu(callback)