from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.modules.residence_calc.keyboards import (
    build_country_kb,
    build_application_type_kb,
)
from app.modules.residence_calc.calculator import calculate_residence_fee
from app.modules.residence_calc.render import render_residence_fee_result

router = Router()


class ResidenceCalcState(StatesGroup):
    choosing_country = State()
    entering_months = State()
    choosing_type = State()

@router.callback_query(F.data == "rescalc:start")
async def open_calc(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ResidenceCalcState.choosing_country)

    await callback.message.edit_text(
        "🧾 Выберите гражданство — рассчитаем стоимость ВНЖ:",
        reply_markup=build_country_kb(),
    )
    await callback.answer()
# Вход в калькулятор
@router.message(F.text.contains("Калькулятор ВНЖ"))
async def start_calc(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ResidenceCalcState.choosing_country)



    await message.answer(
    "🧾 Выберите гражданство — рассчитаем стоимость ВНЖ:",
    reply_markup=build_country_kb(),
    )


# Выбор страны
@router.callback_query(F.data.startswith("rescalc:country:"))
async def select_country(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split(":")[-1]

    await state.update_data(country_code=country_code)
    await state.set_state(ResidenceCalcState.entering_months)

    await callback.message.edit_text(
        "Введите срок ВНЖ в месяцах (например: 12):"
    )
    await callback.answer()


# Ввод месяцев
@router.message(ResidenceCalcState.entering_months)
async def input_months(message: Message, state: FSMContext):
    try:
        months = int(message.text.strip())
        if months < 1 or months > 36:
            raise ValueError
    except Exception:
        await message.answer("Введите число от 1 до 36.")
        return

    await state.update_data(months=months)
    await state.set_state(ResidenceCalcState.choosing_type)

    await message.answer(
        "Тип подачи:",
        reply_markup=build_application_type_kb(),
    )


# Выбор типа
@router.callback_query(F.data.startswith("rescalc:type:"))
async def select_type(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    country_code = data.get("country_code")
    months = data.get("months")

    is_first = callback.data.endswith("first")

    result = calculate_residence_fee(
        country_code=country_code,
        months=months,
        is_first_application=is_first,
    )

    text = render_residence_fee_result(result)

    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Рассчитать ещё", callback_data="rescalc:start")
    kb.button(text="⬅️ В меню", callback_data="rescalc:back:menu")
    kb.adjust(1)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

    await callback.answer()
    await state.clear()

@router.callback_query(F.data == "rescalc:back:menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    from app.handlers.start import build_main_menu
    from app.modules.core.language.service import get_user_lang

    lang = get_user_lang(callback.from_user.id) or "ru"

    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=build_main_menu(lang),
    )
    await callback.answer()

@router.callback_query(F.data == "rescalc:back:country")
async def back_to_country(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResidenceCalcState.choosing_country)

    from app.modules.residence_calc.keyboards import build_country_kb

    await callback.message.edit_text(
        "🧾 Выберите гражданство — рассчитаем стоимость ВНЖ:",
        reply_markup=build_country_kb(),
    )

    await callback.answer()