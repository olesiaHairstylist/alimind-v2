from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_partner_disable_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, выключить", callback_data="partner:disable:confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="partner:disable:cancel"),
        ]
    ])


def build_partner_update_field_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="title", callback_data="partner:update:field:title")],
        [InlineKeyboardButton(text="description_short", callback_data="partner:update:field:description_short")],
        [InlineKeyboardButton(text="description_full", callback_data="partner:update:field:description_full")],
        [InlineKeyboardButton(text="location", callback_data="partner:update:field:location")],
        [InlineKeyboardButton(text="contact", callback_data="partner:update:field:contact")],
        [InlineKeyboardButton(text="languages", callback_data="partner:update:field:languages")],
        [InlineKeyboardButton(text="is_partner", callback_data="partner:update:field:is_partner")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="partner:update:cancel")],
    ])


def build_partner_update_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="partner:update:confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="partner:update:cancel"),
        ]
    ])