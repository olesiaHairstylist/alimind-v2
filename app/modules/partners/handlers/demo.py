from __future__ import annotations

from app.modules.partners.render.text import render_partner_offers
from app.modules.partners.services.post_offers import build_partner_offers_result


def run_demo() -> str:
    context = {
        "destination_airport": "SVO",
        "lang": "en",
    }
    result = build_partner_offers_result(
        context=context,
        has_ticket_result=True,
    )
    return render_partner_offers(result)


def main() -> int:
    print(run_demo())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
