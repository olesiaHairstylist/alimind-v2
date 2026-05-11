from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.modules.admin.access import is_admin_user
from app.modules.city_events.services.health_snapshot_reader import read_health_snapshot
from app.modules.city_events.render.health_render import render_health_snapshot

router = Router()


@router.message(Command("admin_health"))
async def admin_health_handler(message: Message):
    user = message.from_user
    if not user or not is_admin_user(user.id):
        return

    snapshot = read_health_snapshot()
    text = render_health_snapshot(snapshot)

    await message.answer(text)


@router.callback_query(F.data == "admin:health")
async def admin_health_button(callback: CallbackQuery):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        return

    snapshot = read_health_snapshot()
    text = render_health_snapshot(snapshot)

    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "photo:add")
async def admin_photo_add_button(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        await callback.answer()
        return

    from app.modules.directory.handlers.partner_add import PartnerPhotoStates

    await state.clear()
    await state.set_state(PartnerPhotoStates.waiting_id)

    await callback.message.answer("📸 Введите ID партнёра:")
    await callback.answer()