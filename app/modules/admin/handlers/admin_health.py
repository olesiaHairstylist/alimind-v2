from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.modules.city_events.services.health_snapshot_reader import read_health_snapshot
from app.modules.city_events.render.health_render import render_health_snapshot


router = Router()


@router.message(Command("admin_health"))
async def admin_health_handler(message: Message):
    snapshot = read_health_snapshot()
    text = render_health_snapshot(snapshot)

    await message.answer(text)