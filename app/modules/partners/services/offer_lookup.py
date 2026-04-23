from __future__ import annotations

from app.modules.partners.normalize.offers import normalize_partner_offers
from app.modules.partners.source.reader import load_raw_partner_files


def get_partner_offer_by_id(partner_id: str, lang: str = "en") -> dict | None:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return None

    offers = normalize_partner_offers(load_raw_partner_files(), lang=lang)
    for offer in offers:
        if offer["id"] != normalized_partner_id:
            continue
        if offer["status"] != "active" or offer["is_partner"] is not True:
            return None
        return offer

    return None


def build_partner_action_text(offer: dict, lang: str = "en") -> str:
    _ = lang
    action_type = str(offer.get("action_type", "")).strip().lower()
    action_value = str(offer.get("action_value", "")).strip()
    title = str(offer.get("offer_title", "")).strip()

    if not action_value:
        return "Partner action is unavailable."

    if action_type == "url":
        return f"{title}\n{action_value}".strip()

    if action_type == "telegram":
        return f"{title}\nTelegram: {action_value}".strip()

    if action_type == "phone":
        return f"{title}\nPhone: {action_value}".strip()

    if action_type == "whatsapp":
        return f"{title}\nWhatsApp: {action_value}".strip()

    return f"{title}\n{action_value}".strip()

