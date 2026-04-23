from __future__ import annotations

from typing import Any

from app.modules import normalize_electricity_payload
from app.modules import render_city_event_card


def render_electricity_cards(payload: dict[str, Any]) -> str:
    cards = normalize_electricity_payload(payload)

    if not cards:
        return "⚡ Отключения электричества\n\nДанных на сегодня нет."

    parts: list[str] = []

    for idx, card in enumerate(cards, start=1):
        parts.append(f"{idx}.\n{render_city_event_card(card)}")

    return "\n\n".join(parts)
