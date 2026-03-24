from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery

from app.modules.directory.category_menu import build_directory_category_menu
from app.modules.directory.object_list import build_object_list
from app.modules.directory.card_view import load_object_by_id, render_object_card
from app.modules.directory.card_view import (
    load_object_by_id,
    render_object_card,
    build_object_card_kb,
)
router = Router()


@router.callback_query(lambda c: c.data == "main:directory")
async def open_directory_menu(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Услуги",
        reply_markup=build_directory_category_menu(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("dir:"))
async def open_directory_category(callback: CallbackQuery) -> None:
    category = callback.data.split(":", 1)[1]

    await callback.message.answer(
        "Список услуг:",
        reply_markup=build_object_list(category),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("obj:"))
async def open_directory_object(callback: CallbackQuery) -> None:
    object_id = callback.data.split(":", 1)[1]
    obj = load_object_by_id(object_id)

    if obj is None:
        await callback.message.answer("Карточка не найдена.")
    await callback.message.answer(
        render_object_card(obj),
        reply_markup=build_object_card_kb()
    )

    await callback.answer()