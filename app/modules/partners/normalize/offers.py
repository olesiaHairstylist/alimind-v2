from __future__ import annotations

from typing import Any

from app.modules.partners.contracts.partner_offer import PartnerOffer

ALLOWED_STATUSES: set[str] = {"active", "disabled", "draft"}


def _get_text(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        localized = value.get(lang) or value.get("en") or value.get("ru") or value.get("tr")
        return str(localized or "").strip()

    if isinstance(value, str):
        return value.strip()

    return ""


def _normalize_priority(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_status(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    status = value.strip().lower()
    if status not in ALLOWED_STATUSES:
        return None

    return status


def _build_offer(raw_offer: dict[str, Any], lang: str) -> PartnerOffer | None:
    offer_id = str(raw_offer.get("id", "")).strip()
    category = str(raw_offer.get("category", "")).strip()
    subcategory = str(raw_offer.get("subcategory", "")).strip()
    status = _normalize_status(raw_offer.get("status"))
    is_partner = raw_offer.get("is_partner")
    offer_title = _get_text(raw_offer.get("offer_title"), lang)
    offer_text = _get_text(raw_offer.get("offer_text"), lang)
    action_type = str(raw_offer.get("action_type", "")).strip()
    action_value = str(raw_offer.get("action_value", "")).strip()
    priority = _normalize_priority(raw_offer.get("priority"))

    if not offer_id:
        return None
    if not category or not subcategory:
        return None
    if status is None:
        return None
    if not isinstance(is_partner, bool):
        return None
    if not offer_title or not offer_text:
        return None
    if not action_type or not action_value:
        return None
    if priority is None:
        return None

    return {
        "id": offer_id,
        "category": category,
        "subcategory": subcategory,
        "status": status,
        "is_partner": is_partner,
        "offer_title": offer_title,
        "offer_text": offer_text,
        "action_type": action_type,
        "action_value": action_value,
        "priority": priority,
    }


def normalize_partner_offers(raw_offers: list[dict[str, Any]], lang: str) -> list[PartnerOffer]:
    offers: list[PartnerOffer] = []

    for raw_offer in raw_offers:
        if not isinstance(raw_offer, dict):
            continue

        offer = _build_offer(raw_offer, lang)
        if offer is not None:
            offers.append(offer)

    return offers
