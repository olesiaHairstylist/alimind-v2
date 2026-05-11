from aiogram.types import Message


async def log_moderation_action(message: Message, reason: str):
    print(
        f"[GROUP MODERATION] deleted message | "
        f"chat={message.chat.id} | "
        f"user={message.from_user.id if message.from_user else 'unknown'} | "
        f"reason={reason}"
    )