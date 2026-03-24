from __future__ import annotations
from app.modules.directory.router import router as directory_router
import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers.start import router as start_router
from app.modules.city_events.ui.router import router as city_events_router
from app.modules.core.language.handler import router as language_router
from app.modules.city_events.services.updater import (
    update_emergency_contacts,
    update_pharmacies,
)


async def main() -> None:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    update_emergency_contacts()
    update_pharmacies()

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(directory_router)
    dp.include_router(city_events_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())