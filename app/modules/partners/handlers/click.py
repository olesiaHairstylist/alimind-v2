from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.modules.partners.contracts.callbacks import parse_partner_click_cb
from app.modules.partners.services.ab_test import (
    get_engagement_ab_group,
    get_engagement_weight,
)
from app.modules.partners.services.engagement import mark_click
from app.modules.partners.services.offer_lookup import (
    build_partner_action_text,
    get_partner_offer_by_id,
)
from app.modules.partners.storage.click_events_memory import mark_partner_click_event
from app.modules.partners.storage.impressions_memory import (
    find_latest_matching_impression_event_id,
)

router = Router()


@router.callback_query(F.data.startswith("partner:click:"))
async def handle_partner_click(callback: CallbackQuery) -> None:
    partner_id = parse_partner_click_cb(callback.data)
    if not partner_id:
        await callback.answer("Partner action is unavailable.", show_alert=False)
        return

    lang = "en"
    user = callback.from_user
    user_key = str(user.id) if user else "unknown"
    session_key = ""

    tracked = mark_click(user_key=user_key, partner_id=partner_id)
    impression_event_id = find_latest_matching_impression_event_id(
        user_key=user_key,
        partner_id=partner_id,
        session_key=session_key,
    )

    try:
        mark_partner_click_event(
            user_key=user_key,
            session_key=session_key,
            partner_id=partner_id,
            ab_group=get_engagement_ab_group(user_key),
            engagement_weight=get_engagement_weight(user_key),
            impression_event_id=impression_event_id,
        )
    except Exception:
        pass

    offer = get_partner_offer_by_id(partner_id=partner_id, lang=lang)
    if offer is None:
        await callback.answer("Partner offer is no longer available.", show_alert=False)
        return

    action_text = build_partner_action_text(offer, lang=lang)

    try:
        await callback.message.answer(action_text)
    finally:
        await callback.answer("Opening partner offer." if tracked else "Opening partner offer without tracking.")
