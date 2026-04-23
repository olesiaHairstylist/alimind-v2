from __future__ import annotations

from typing import Any


TEXTS = {
    "ru": {
        "title": "Partner Loader V1",
        "context": "Контекст",
        "destination": "Аэропорт назначения",
        "eligible": "Подходящих партнёрских предложений",
        "source": "Файлов источника",
        "normalized": "Нормализовано",
        "empty": "После результата билетов полезных партнёрских предложений пока нет.",
        "action": "Действие",
        "partner": "Партнёрское предложение",
    },
    "en": {
        "title": "Partner Loader V1",
        "context": "Context",
        "destination": "Destination airport",
        "eligible": "Eligible partner offers",
        "source": "Source files",
        "normalized": "Normalized",
        "empty": "No helpful partner offers are available after the ticket result yet.",
        "action": "Action",
        "partner": "Partner offer",
    },
    "tr": {
        "title": "Partner Loader V1",
        "context": "Baglam",
        "destination": "Varis havalimani",
        "eligible": "Uygun partner teklifleri",
        "source": "Kaynak dosyalari",
        "normalized": "Normalize edilenler",
        "empty": "Bilet sonucundan sonra gosterilecek uygun partner teklifi simdilik yok.",
        "action": "Aksiyon",
        "partner": "Partner teklifi",
    },
}


def _texts(lang: str) -> dict[str, str]:
    return TEXTS.get(lang, TEXTS["en"])


def render_partner_offers(result: dict[str, Any]) -> str:
    context = result["context"]
    lang = context["lang"]
    texts = _texts(lang)

    lines = [
        texts["title"],
        f"{texts['destination']}: {context['destination_airport']}",
        f"{texts['source']}: {result['source_count']}",
        f"{texts['normalized']}: {result['normalized_count']}",
        f"{texts['eligible']}: {result['eligible_count']}",
        "",
    ]

    offers = result["offers"]
    if not offers:
        lines.append(texts["empty"])
        return "\n".join(lines).strip()

    for index, offer in enumerate(offers, start=1):
        lines.append(f"{index}. [{offer['subcategory']}] {offer['offer_title']}")
        lines.append(offer["offer_text"])
        lines.append(f"{texts['action']}: {offer['action_type']} -> {offer['action_value']}")
        lines.append(f"{texts['partner']}: {offer['id']} | priority={offer['priority']}")
        lines.append("")

    return "\n".join(lines).strip()

