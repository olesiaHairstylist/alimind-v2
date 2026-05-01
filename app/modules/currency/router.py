from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from app.modules.currency.service import fetch_rates_to_try

router = Router()


class CurrencyState(StatesGroup):
    waiting_amount = State()


def build_currency_menu():
    b = InlineKeyboardBuilder()
    b.button(text="💱 Конвертировать", callback_data="currency:convert")
    b.button(text="📊 Курс валют", callback_data="currency:rates")
    b.button(text="⬅️ Назад", callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()
def build_currency_input_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Назад к валюте", callback_data="currency:menu")
    b.button(text="🏠 Главное меню", callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()

@router.callback_query(lambda c: c.data == "currency:menu")
async def currency_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💱 Валюта\n\nВыберите действие:",
        reply_markup=build_currency_menu(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "currency:rates")
async def currency_rates(callback: CallbackQuery):
    try:
        rates = await fetch_rates_to_try()
        try_to_rub = 1 / rates["RUB"]
        text = (
            "📊 Курс валют (к лире)\n\n"
            f"1 USD → {rates['USD']:.2f} TRY\n"
            f"1 EUR → {rates['EUR']:.2f} TRY\n"
            f"1 RUB → {rates['RUB']:.4f} TRY\n\n"
            f"💡 1 TRY → {try_to_rub:.2f} RUB\n\n"
            "🔄 Данные обновлены при запросе"
        )

    except Exception:
        text = "⚠️ Не удалось получить курс. Попробуйте позже."

    try:
        await callback.message.edit_text(text, reply_markup=build_currency_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(lambda c: c.data == "currency:convert")
async def currency_convert_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CurrencyState.waiting_amount)
    await callback.message.edit_text(
        "✍️ Введите сумму:\n\n"
        "Примеры:\n"
        "135 usd\n"
        "557 eur\n"
        "1850 rub",
        reply_markup=build_currency_input_kb(),
    )
    await callback.answer()


@router.message(CurrencyState.waiting_amount)
async def currency_convert_amount(message: Message, state: FSMContext):
    raw = (message.text or "").strip().lower().replace(",", ".")
    parts = raw.split()

    if len(parts) != 2:
        await message.answer("Введите так: 135 usd / 557 eur / 1850 rub")
        return

    amount_text, currency_text = parts

    try:
        amount = float(amount_text)
    except ValueError:
        await message.answer("Сумма должна быть числом")
        return

    currency = currency_text.upper()

    try:
        rates = await fetch_rates_to_try()
    except Exception:
        await message.answer("⚠️ Не удалось получить курс")
        return

    if currency not in rates:
        await message.answer("Доступно: USD, EUR, RUB")
        return

    result = amount * rates[currency]

    await state.clear()

    await message.answer(
        f"💱 Расчёт\n\n"
        f"{amount:g} {currency} → {result:.2f} TRY\n\n"
        f"Курс: 1 {currency} = {rates[currency]:.4f} TRY",
        reply_markup=build_currency_menu(),
    )