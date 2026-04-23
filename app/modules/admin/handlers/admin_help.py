from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.modules.admin.access import is_admin_user

router = Router()


@router.message(Command("admin_help"))
async def admin_help_handler(message: Message):
    user = message.from_user
    if not user or not is_admin_user(user.id):
        return

    await message.answer(
        "Admin commands:\n\n"
        "/admin_health - system health\n"
        "/click_signal <partner_id> - click signal diagnostic"
    )
