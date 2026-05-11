from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.admin.access import is_admin_user

router = Router()


@router.message(Command("admin"))
async def admin_menu_handler(message: Message):
    user = message.from_user
    if not user or not is_admin_user(user.id):
        return

    kb = InlineKeyboardBuilder()

    kb.button(text="📊 Аналитика", callback_data="admin:analytics")
    kb.button(text="🧭 Путь пользователя", callback_data="admin:flow")
    kb.button(text="⚠️ Health / Watchdog", callback_data="admin:health")
    kb.button(text="🚪 Точки выхода", callback_data="admin:exits")

    # вот сюда добавляем
    kb.button(text="➕ Добавить карточку", callback_data="...")
    kb.button(text="📸 Добавить фото", callback_data="photo:add")

    kb.adjust(1)

    await message.answer(
        "⚙️ Админ-панель AliMind\n\nВыберите раздел:",
        reply_markup=kb.as_markup(),
    )
