from __future__ import annotations

from typing import Any

from app.modules.partners.contracts.match_context import PartnerMatchContext
from app.modules.partners.normalize.offers import normalize_partner_offers
from app.modules.partners.rules.eligibility import filter_eligible_partner_offers
from app.modules.partners.select.offers import select_partner_offers
from app.modules.partners.source.reader import load_raw_partner_files


def build_partner_offers_result(
    context: PartnerMatchContext,
    has_ticket_result: bool,
) -> dict[str, Any]:
    raw_offers = load_raw_partner_files()
    normalized_offers = normalize_partner_offers(raw_offers, context["lang"])
    eligible_offers = filter_eligible_partner_offers(
        normalized_offers,
        context=context,
        has_ticket_result=has_ticket_result,
    )
    selected_offers = select_partner_offers(eligible_offers)

    return {
        "has_ticket_result": has_ticket_result,
        "context": context,
        "source_count": len(raw_offers),
        "normalized_count": len(normalized_offers),
        "eligible_count": len(eligible_offers),
        "offers": selected_offers,
    }

