from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.handlers.start import router as start_router

from app.modules.sea_status.handlers import router as sea_status_router
from app.modules.admin.handlers.admin_health import router as admin_health_router
from app.modules.admin.handlers.admin_help import router as admin_help_router
from app.modules.city_events.services.updater import (
    update_emergency_contacts,
    update_pharmacies,
)
from app.modules.city_events.ui.router import router as city_events_router
from app.modules.core.language.handler import router as language_router
from app.modules.directory.router import router as directory_router
from app.modules.phrasebook.router import router as phrasebook_router
from app.modules.maps.handlers import router as maps_router
from app.modules.watchdog.service import run_watchdog


from app.modules.partners.handlers.tickets_preview_click import (
    router as tickets_preview_partner_click_router,
)

async def main() -> None:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    await bot.set_my_commands([
        BotCommand(command="tickets_preview", description="Preview tickets with partner block"),
        BotCommand(command="admin_help", description="Админ-справка"),
        BotCommand(command="admin_health", description="Состояние системы"),
        BotCommand(command="language", description="Выбрать язык"),
        BotCommand(command="add_partner", description="Добавить партнёра"),
        BotCommand(command="partner_check", description="Проверить партнёра"),
        BotCommand(command="partner_disable", description="Отключить партнёра"),
        BotCommand(command="partner_update", description="Обновить партнёра"),
        BotCommand(command="partner_photo", description="Добавить фото партнёру"),
    ])

    update_emergency_contacts()
    update_pharmacies()

    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(directory_router)
    dp.include_router(sea_status_router)
    dp.include_router(maps_router)
    dp.include_router(phrasebook_router)
    dp.include_router(tickets_preview_partner_click_router)
    dp.include_router(city_events_router)
    dp.include_router(admin_health_router)


    dp.include_router(admin_help_router)

    await run_watchdog(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
