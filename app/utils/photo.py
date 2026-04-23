from pathlib import Path
from aiogram.types import Message
from aiogram import Bot

DATA_PATH = Path("app/data/objects")

async def save_object_photo(message: Message, object_id: str, bot: Bot) -> str | None:
    if not message.photo:
        return None

    photo = message.photo[-1]  # самое большое качество
    file = await bot.get_file(photo.file_id)

    folder = DATA_PATH / object_id
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / "photo.jpg"

    await bot.download_file(file.file_path, destination=file_path)

    return str(file_path)