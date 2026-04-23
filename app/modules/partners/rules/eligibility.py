from __future__ import annotations

from app.modules.partners.contracts.match_context import PartnerMatchContext
from app.modules.partners.contracts.partner_offer import PartnerOffer

ALLOWED_SUBCATEGORIES: set[str] = {"insurance", "transfer", "esim"}


def _get_route_airports(context: PartnerMatchContext) -> set[str]:
    route = str(context.get("route", "")).strip().upper()
    if not route:
        return set()

    return {part.strip() for part in route.split("-") if part.strip()}


def _matches_geo(
    offer: PartnerOffer,
    context: PartnerMatchContext,
) -> bool:
    _ = offer
    country_from = str(context.get("country_from", "")).strip().upper()
    country_to = str(context.get("country_to", "")).strip().upper()
    route_airports = _get_route_airports(context)
    destination_airport = str(context.get("destination_airport", "")).strip().upper()

    if destination_airport:
        route_airports.add(destination_airport)

    if not country_from and not country_to and not route_airports:
        return True

    return True


def _has_destination_airport(context: PartnerMatchContext) -> bool:
    return bool(str(context.get("destination_airport", "")).strip())


def _is_subcategory_allowed(
    offer: PartnerOffer,
    context: PartnerMatchContext,
) -> bool:
    subcategory = offer["subcategory"]

    if subcategory == "insurance":
        return True

    if subcategory == "transfer":
        return _has_destination_airport(context)

    if subcategory == "esim":
        return True

    return False


def filter_eligible_partner_offers(
    offers: list[PartnerOffer],
    context: PartnerMatchContext,
    has_ticket_result: bool,
) -> list[PartnerOffer]:
    if not has_ticket_result:
        return []

    return [
        offer
        for offer in offers
        if offer["status"] == "active"
        and offer["is_partner"] is True
        and offer["subcategory"] in ALLOWED_SUBCATEGORIES
        and _matches_geo(offer, context)
        and _is_subcategory_allowed(offer, context)
    ]
