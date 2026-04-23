from __future__ import annotations

from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .keyboard import build_partner_disable_confirm_kb
from .service import (
    fetch_partner_by_id,
    send_partner_to_api,
)
from .states import (
    PartnerCheckStates,
    PartnerDisableStates,
)

router = Router()


def render_partner_card(obj: dict[str, Any]) -> str:
    title = obj.get("title", "Без названия")
    partner_id = obj.get("id", "-")
    category = obj.get("category", "-")
    subcategory = obj.get("subcategory", "-")
    description_short = obj.get("description_short", "")
    description_full = obj.get("description_full", "")
    location = obj.get("location", "")
    contact = obj.get("contact", "")
    languages = obj.get("languages", [])
    is_partner = obj.get("is_partner", False)

    if isinstance(languages, list):
        languages_text = ", ".join(languages) if languages else "-"
    else:
        languages_text = str(languages)

    status_text = "✅ ACTIVE" if is_partner is True else "⛔ DISABLED"

    parts = [
        f"<b>{title}</b>",
        f"ID: <code>{partner_id}</code>",
        f"Category: {category}",
        f"Subcategory: {subcategory}",
        f"Status: {status_text}",
    ]

    if description_short:
        parts.append(f"\n{description_short}")

    if description_full:
        parts.append(f"\n{description_full}")

    if location:
        parts.append(f"\n📍 {location}")

    if contact:
        parts.append(f"📞 {contact}")

    parts.append(f"🌐 Languages: {languages_text}")

    return "\n".join(parts)


def render_partner_status(obj: dict[str, Any]) -> str:
    is_partner = obj.get("is_partner") is True
    return "Статус: ✅ partner ACTIVE" if is_partner else "Статус: ⛔ partner DISABLED"


def build_disabled_partner_obj(obj: dict[str, Any]) -> dict[str, Any]:
    updated = dict(obj)
    updated["is_partner"] = False
    return updated


def extract_api_result_message(result: Any) -> str:
    if isinstance(result, dict):
        ok = result.get("ok")
        status_code = result.get("status_code")
        text = result.get("text") or result.get("message") or ""

        if ok is True:
            if status_code:
                return f"OK ({status_code})"
            return "OK"

        if ok is False:
            if status_code and text:
                return f"ERROR ({status_code}): {text}"
            if status_code:
                return f"ERROR ({status_code})"
            if text:
                return f"ERROR: {text}"
            return "ERROR"

    return str(result)


# =========================================================
# STEP 1 — /partner_check
# =========================================================
@router.message(Command("partner_check"))
async def partner_check_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PartnerCheckStates.waiting_partner_id)
    await message.answer("Введите partner id для проверки.")


@router.message(PartnerCheckStates.waiting_partner_id)
async def partner_check_receive_id(message: Message, state: FSMContext) -> None:
    partner_id = (message.text or "").strip()

    if not partner_id:
        await message.answer("ID пустой. Введите partner id.")
        return

    obj = fetch_partner_by_id(partner_id)

    if not obj:
        await state.clear()
        await message.answer(f"Партнёр с id '{partner_id}' не найден.")
        return

    await message.answer("Объект найден:")
    await message.answer(render_partner_card(obj), parse_mode="HTML")
    await message.answer(render_partner_status(obj))

    await state.clear()


# =========================================================
# STEP 2 — /partner_disable
# =========================================================
@router.message(Command("partner_disable"))
async def partner_disable_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PartnerDisableStates.waiting_partner_id)
    await message.answer("Введите partner id для отключения.")


@router.message(PartnerDisableStates.waiting_partner_id)
async def partner_disable_receive_id(message: Message, state: FSMContext) -> None:
    partner_id = (message.text or "").strip()

    if not partner_id:
        await message.answer("ID пустой. Введите partner id.")
        return

    obj = fetch_partner_by_id(partner_id)

    if not obj:
        await state.clear()
        await message.answer(f"Партнёр с id '{partner_id}' не найден.")
        return

    await state.update_data(partner_id=partner_id, partner_obj=obj)
    await state.set_state(PartnerDisableStates.waiting_confirm_disable)

    await message.answer("Найден объект. Подтвердите отключение:")
    await message.answer(
        render_partner_card(obj),
        reply_markup=build_partner_disable_confirm_kb(),
        parse_mode="HTML",
    )


@router.callback_query(
    F.data == "partner:disable:confirm",
    PartnerDisableStates.waiting_confirm_disable,
)
async def partner_disable_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    obj = data.get("partner_obj")

    if not obj:
        await state.clear()
        await callback.message.answer("Ошибка: объект не найден в текущей сессии.")
        await callback.answer()
        return

    updated_obj = build_disabled_partner_obj(obj)
    result = send_partner_to_api(updated_obj)

    await state.clear()

    if isinstance(result, dict) and result.get("ok") is True:
        await callback.message.answer("Партнёр отключён: is_partner=false")
        await callback.message.answer(render_partner_card(updated_obj), parse_mode="HTML")
        await callback.message.answer(render_partner_status(updated_obj))
    else:
        await callback.message.answer(
            "Ошибка при сохранении:\n"
            f"{extract_api_result_message(result)}"
        )

    await callback.answer()


@router.callback_query(
    F.data == "partner:disable:cancel",
    PartnerDisableStates.waiting_confirm_disable,
)
async def partner_disable_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Отключение отменено.")
    await callback.answer()