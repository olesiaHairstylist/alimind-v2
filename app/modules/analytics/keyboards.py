from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.modules.analytics.report import get_recent_users


def build_recent_users_kb(limit: int = 10) -> InlineKeyboardMarkup:
    users = get_recent_users(limit=limit)

    buttons = []

    for user_id in users:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {user_id}",
                callback_data=f"admin:flow:user:{user_id}",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)