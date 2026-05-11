from aiogram import Router, F
from aiogram.types import Message

from app.modules.group_moderation.rules import check_group_message
from app.modules.group_moderation.logger import log_moderation_action

router = Router(name="group_moderation_handlers")


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_moderation(message: Message):

    text = message.text or ""

    result = check_group_message(text)

    if not result["delete"]:
        return

    try:
        await message.delete()

        await log_moderation_action(
            message=message,
            reason=result["reason"],
        )

    except Exception as e:
        print(f"[GROUP MODERATION ERROR] {e}")