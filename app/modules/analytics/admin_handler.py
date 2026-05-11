from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.modules.admin.access import is_admin_user

from pathlib import Path
from app.modules.analytics.report import (
    build_analytics_report,
    build_user_flow_report,
    build_exit_points_report,
)
router = Router()
class PhotoAddState(StatesGroup):
    waiting_object_id = State()
    waiting_photo = State()

@router.message(Command("admin_analytics"))
async def admin_analytics_handler(message: Message):
    user = message.from_user

    if not user or not is_admin_user(user.id):
        return

    text = build_analytics_report()
    await message.answer(text)

@router.message(Command("admin_flow"))
async def admin_flow_handler(message: Message):
    user = message.from_user

    if not user or not is_admin_user(user.id):
        return

    text = build_user_flow_report()
    await message.answer(text)
@router.callback_query(F.data == "admin:analytics")
async def admin_analytics_button(callback: CallbackQuery):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        return

    text = build_analytics_report()
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "admin:flow")
async def admin_flow_button(callback: CallbackQuery):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        return

    text = build_user_flow_report()
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "admin:exits")
async def admin_exits_button(callback: CallbackQuery):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        return

    text = build_exit_points_report()
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "admin:health")
async def admin_health_button(callback: CallbackQuery):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        await callback.answer()
        return

    await callback.message.answer("⚠️ Health / Watchdog пока не подключён.")
    await callback.answer()


@router.callback_query(F.data == "photo:add")
async def admin_photo_add_button(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    if not user or not is_admin_user(user.id):
        await callback.answer()
        return

    # 🔥 запускаем старый сценарий


    await state.clear()


    await callback.message.answer("📸 Отправьте фото карточки:")
    await callback.answer()

OBJECTS_PATH = Path("app/data/objects")


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
