from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.partners.contracts.callbacks import build_partner_click_cb


def build_partner_keyboard(offers: list[dict]) -> InlineKeyboardMarkup | None:
    if not offers:
        return None

    builder = InlineKeyboardBuilder()

    for offer in offers:
        title = str(offer.get("offer_title", "")).strip()
        partner_id = str(offer.get("id", "")).strip()
        if not title or not partner_id:
            continue

        builder.button(
            text=title,
            callback_data=build_partner_click_cb(partner_id),
        )

    if not builder.buttons:
        return None

    builder.adjust(1)
    return builder.as_markup()

