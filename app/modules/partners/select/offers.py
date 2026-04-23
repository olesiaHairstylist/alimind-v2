from __future__ import annotations

from app.modules.partners.contracts.partner_offer import PartnerOffer


def select_partner_offers(offers: list[PartnerOffer]) -> list[PartnerOffer]:
    sorted_offers = sorted(
        offers,
        key=lambda offer: (-int(offer["priority"]), str(offer["id"])),
    )

    selected: list[PartnerOffer] = []
    seen_subcategories: set[str] = set()

    for offer in sorted_offers:
        subcategory = offer["subcategory"]
        if subcategory in seen_subcategories:
            continue

        selected.append(offer)
        seen_subcategories.add(subcategory)

        if len(selected) >= 3:
            break

    return selected

