

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.modules.group_bridge.real_estate_to_group import publish_real_estate_to_group
router = Router()
print("GROUP BRIDGE MODULE LOADED")
GROUP_ID = -1005236570046

@router.message(Command("post_real_estate"))
async def post_real_estate(message: Message):

    result = await publish_real_estate_to_group(
        message.bot
    )

    if result:
        await message.answer(
            "✅ Объекты отправлены в группу"
        )
    else:
        await message.answer(
            "📭 Новых объектов для публикации нет"
        )
@router.message()
async def group_test(message: Message):

    if message.chat.id != GROUP_ID:
        return

    await message.answer("✅ Бот видит группу")

    print(
        "GROUP OK:",
        message.chat.id,
        message.text
    )

