from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.modules.directory.services.loader import load_object_by_id

router = Router()

MAPS_OPEN_PREFIX = "maps:open:"


@router.callback_query(F.data.startswith(MAPS_OPEN_PREFIX))
async def open_maps_handler(callback: CallbackQuery) -> None:
    object_id = callback.data.replace(MAPS_OPEN_PREFIX, "", 1)

    obj = load_object_by_id(object_id)
    if not obj:
        await callback.answer("Объект не найден", show_alert=True)
        return

    lat = obj.get("lat")
    lng = obj.get("lng")

    if not lat or not lng:
        await callback.answer("Координаты не указаны", show_alert=True)
        return

    maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

    await callback.message.answer(f"📍 Как добраться:\n{maps_url}")

    await callback.message.answer_location(
        latitude=float(lat),
        longitude=float(lng),
    )

    await callback.answer()