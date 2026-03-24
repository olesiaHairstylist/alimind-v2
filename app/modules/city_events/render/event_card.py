from __future__ import annotations

from app.modules.city_events.contracts.event_card import CityEventCard


def render_city_event_card(event: CityEventCard) -> str:
    lines: list[str] = []

    if event["category"] == "electricity":
        lines.append("⚡ Отключение электричества")
    elif event["category"] == "water":
        lines.append("💧 Отключение воды")
    else:
        lines.append("📍 Событие города")

    lines.append("")

    if event["area"]:
        lines.append(f"📍 Район: {event['area']}")

    if event["status"] == "planned":
        lines.append("📌 Статус: плановое")
    elif event["status"] == "emergency":
        lines.append("📌 Статус: аварийное")
    elif event["status"]:
        lines.append(f"📌 Статус: {event['status']}")

    if event["start_at"]:
        lines.append(f"🕒 Начало: {event['start_at']}")

    if event["end_at"]:
        lines.append(f"🕓 Окончание: {event['end_at']}")

    if event["note"]:
        lines.append("")
        lines.append(f"ℹ️ Примечание: {event['note']}")

    if event["updated_at"]:
        lines.append(f"🔄 Обновлено: {event['updated_at']}")

    if event["source_name"]:
        lines.append(f"🏢 Источник: {event['source_name']}")

    return "\n".join(lines)