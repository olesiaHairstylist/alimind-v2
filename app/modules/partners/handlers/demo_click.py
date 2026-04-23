from __future__ import annotations

from app.modules.partners.render.keyboard import build_partner_keyboard
from app.modules.partners.services.engagement import mark_click
from app.modules.partners.services.offer_lookup import (
    build_partner_action_text,
    get_partner_offer_by_id,
)
from app.modules.partners.services.revenue_engine import build_revenue_offers_result
from app.modules.partners.storage.engagement_memory import (
    clear_click_memory,
    get_click_memory,
)


def main() -> int:
    user_key = "123456"
    clear_click_memory(user_key)

    result = build_revenue_offers_result(
        context={
            "route": "AYT-SVO",
            "country_from": "TR",
            "country_to": "RU",
            "destination_airport": "SVO",
            "lang": "en",
            "user_key": user_key,
            "session_key": "demo_click_session",
        },
        has_ticket_result=True,
    )

    offers = result["offers"]
    keyboard = build_partner_keyboard(offers)

    print("CALLBACK FORMAT:", "partner:click:<partner_id>")
    print("OFFERS:", [offer["id"] for offer in offers])
    print("KEYBOARD:", keyboard.model_dump() if keyboard else None)

    if not offers:
        print("NO OFFERS")
        return 0

    partner_id = offers[0]["id"]
    tracked = mark_click(user_key=user_key, partner_id=partner_id)
    offer = get_partner_offer_by_id(partner_id=partner_id, lang="en")

    print("TRACKED:", tracked)
    print("ACTION:")
    print(build_partner_action_text(offer or {}, lang="en"))
    print("ENGAGEMENT MEMORY:")
    print(get_click_memory(user_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
