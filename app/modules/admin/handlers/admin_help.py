from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

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
        "/admin_flow - user path report\n"
        "/click_signal <partner_id> - click signal diagnostic"
    )
@router.callback_query(F.data == "admin:help")
async def admin_help_button(callback: CallbackQuery):
    user = callback.from_user

    if not user or not is_admin_user(user.id):
        await callback.answer()
        return

    await callback.message.answer(
        "Admin commands:\n\n"
        "/admin_health - system health\n"
        "/admin_flow - user path report\n"
        "/admin_analytics - analytics overview\n"
        "/click_signal <partner_id> - click signal diagnostic"
    )

    await callback.answer()