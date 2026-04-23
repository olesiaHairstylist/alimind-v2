from __future__ import annotations

from typing import Any

from app.modules.partners.services.revenue_engine import build_revenue_offers_result

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "heading": "Полезно для поездки:",
        "transfer": "Трансфер",
        "insurance": "Страховка",
        "esim": "Интернет",
        "partner": "Партнерское предложение",
    },
    "en": {
        "heading": "Useful for your trip:",
        "transfer": "Transfer",
        "insurance": "Insurance",
        "esim": "Internet",
        "partner": "Partner offer",
    },
    "tr": {
        "heading": "Yolculuk icin faydali olabilir:",
        "transfer": "Transfer",
        "insurance": "Sigorta",
        "esim": "Internet",
        "partner": "Partner teklifi",
    },
}


def _texts(lang: str) -> dict[str, str]:
    return TEXTS.get(lang, TEXTS["en"])


def _get_route_airports(context: dict[str, Any]) -> list[str]:
    route = str(context.get("route", "")).strip().upper()
    if not route:
        return []

    return [part.strip() for part in route.split("-") if part.strip()]


def _get_destination_airport(context: dict[str, Any]) -> str:
    explicit_destination = str(context.get("destination_airport", "")).strip().upper()
    if explicit_destination:
        return explicit_destination

    route_airports = _get_route_airports(context)
    return route_airports[-1] if route_airports else ""


def _render_partner_block_text(selected: list[dict[str, Any]], lang: str) -> str:
    if not selected:
        return ""

    texts = _texts(lang)
    lines = [
        "---",
        texts["heading"],
        "",
    ]

    for offer in selected:
        lines.append(f"{texts.get(offer['subcategory'], offer['subcategory'].title())}")
        lines.append(offer["offer_title"])
        lines.append(offer["offer_text"])
        lines.append(texts["partner"])
        lines.append("")

    lines.append("---")
    return "\n".join(lines).strip()


def build_partner_block_payload(context: dict[str, Any]) -> dict[str, Any]:
    try:
        lang = str(context.get("lang", "en")).strip().lower() or "en"
        partner_result = build_revenue_offers_result(
            context={
                "lang": lang,
                "route": str(context.get("route", "")).strip().upper(),
                "country_from": str(context.get("country_from", "")).strip().upper(),
                "country_to": str(context.get("country_to", "")).strip().upper(),
                "date": str(context.get("date", "")).strip(),
                "destination_airport": _get_destination_airport(context),
                "user_key": str(context.get("user_key", "")).strip(),
                "session_key": str(context.get("session_key", "")).strip(),
            },
            has_ticket_result=bool(context.get("has_ticket_result", True)),
        )
        print(f"[PARTNER] loaded: {partner_result['source_count']}")

        selected = partner_result.get("offers", [])

        if not selected:
            print("[PARTNER] rendered: no")
            return {"text": "", "offers": []}

        text = _render_partner_block_text(selected, lang)
        print("[PARTNER] rendered: yes")
        return {
            "text": text,
            "offers": list(selected),
        }
    except Exception:
        print("[PARTNER] rendered: no")
        return {"text": "", "offers": []}


def render_partner_block(context: dict) -> str:
    return str(build_partner_block_payload(context).get("text", "")).strip()
