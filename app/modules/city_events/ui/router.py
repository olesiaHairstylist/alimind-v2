from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.modules.city_events.render.keyboard_render import build_city_events_menu_kb
from app.modules.city_events.ui.callbacks import (
    CITY_EVENTS_BACK_CB,
    CITY_EVENTS_ELECTRICITY_CB,
    CITY_EVENTS_EMERGENCY_CB,
    CITY_EVENTS_MENU_CB,
    CITY_EVENTS_PHARMACIES_CB,
    CITY_EVENTS_WATER_CB,
)
from app.modules.city_events.ui.handlers import (
    open_city_events_menu,
    open_electricity,
    open_emergency,
    open_pharmacies,
    open_water,
)

router = Router()


@router.message(Command("city_events"))
async def city_events_command(message: Message) -> None:
    await message.answer(
        "События города",
        reply_markup=build_city_events_menu_kb(),
    )


router.callback_query.register(open_city_events_menu, lambda c: c.data == CITY_EVENTS_MENU_CB)
router.callback_query.register(open_city_events_menu, lambda c: c.data == CITY_EVENTS_BACK_CB)
router.callback_query.register(open_pharmacies, lambda c: c.data == CITY_EVENTS_PHARMACIES_CB)
router.callback_query.register(open_electricity, lambda c: c.data == CITY_EVENTS_ELECTRICITY_CB)
router.callback_query.register(open_water, lambda c: c.data == CITY_EVENTS_WATER_CB)

router.callback_query.register(open_emergency, lambda c: c.data == CITY_EVENTS_EMERGENCY_CB)
router.callback_query.register(open_emergency, lambda c: c.data == CITY_EVENTS_EMERGENCY_CB)