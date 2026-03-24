from aiogram import Router
from aiogram.types import CallbackQuery
from app.handlers.start import show_main_menu

router = Router()

user_lang: dict[int, str] = {}


@router.callback_query(lambda c: c.data.startswith("lang:"))
async def language_select_handler(callback: CallbackQuery) -> None:
    lang = callback.data.split(":", 1)[1]
    user_lang[callback.from_user.id] = lang
    await show_main_menu(callback)