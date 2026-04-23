from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.service import get_user_lang
from app.modules.partners.services.click_signals import increment_click
from app.modules.partners.services.offer_lookup import (
    build_partner_action_text,
    get_partner_offer_by_id,
)

SOURCE = "tickets_preview"
PARTNER_TICKETS_PREVIEW_CLICK_PREFIX = "partner:tickets_preview:click:"

router = Router()


def build_tickets_preview_partner_click_cb(partner_id: str) -> str:
    return f"{PARTNER_TICKETS_PREVIEW_CLICK_PREFIX}{partner_id}"


def parse_tickets_preview_partner_click_cb(data: str | None) -> str | None:
    raw_data = str(data or "").strip()
    if not raw_data.startswith(PARTNER_TICKETS_PREVIEW_CLICK_PREFIX):
        return None

    partner_id = raw_data[len(PARTNER_TICKETS_PREVIEW_CLICK_PREFIX):].strip()
    return partner_id or None


def build_tickets_preview_partner_keyboard(offers: list[dict]) -> InlineKeyboardMarkup | None:
    if not offers:
        return None

    builder = InlineKeyboardBuilder()

    for offer in offers:
        partner_id = str(offer.get("id", "")).strip()
        title = str(offer.get("offer_title", "")).strip()
        if not partner_id or not title:
            continue

        builder.button(
            text=title,
            callback_data=build_tickets_preview_partner_click_cb(partner_id),
        )

    if not builder.buttons:
        return None

    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith(PARTNER_TICKETS_PREVIEW_CLICK_PREFIX))
async def handle_tickets_preview_partner_click(callback: CallbackQuery) -> None:
    partner_id: str | None = None

    try:
        partner_id = parse_tickets_preview_partner_click_cb(callback.data)
        user = callback.from_user
        user_id = str(user.id) if user else "unknown"

        if partner_id:
            print(f"[CLICK] partner={partner_id} user_id={user_id} source={SOURCE}")
    except Exception:
        pass

    try:
        if partner_id:
            increment_click(partner_id)
    except Exception:
        pass

    try:
        user = callback.from_user
        lang = get_user_lang(user.id) if user else "en"
        offer = get_partner_offer_by_id(partner_id=partner_id or "", lang=lang or "en")
        if offer is not None and callback.message is not None:
            await callback.message.answer(build_partner_action_text(offer, lang=lang or "en"))
    except Exception:
        pass

    try:
        await callback.answer()
    except Exception:
        pass
