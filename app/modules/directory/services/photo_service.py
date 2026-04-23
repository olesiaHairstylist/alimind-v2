from pathlib import Path
from aiogram.types import Message

PHOTO_PATH = Path("app/data/object_photos")


async def save_object_photo(message: Message, object_id: str, bot):
    if not message.photo:
        return None

    PHOTO_PATH.mkdir(parents=True, exist_ok=True)

    file = message.photo[-1]  # самое большое фото
    file_info = await bot.get_file(file.file_id)

    save_path = PHOTO_PATH / f"{object_id}.jpg"
    await bot.download_file(file_info.file_path, destination=save_path)

    return save_path.as_posix()
