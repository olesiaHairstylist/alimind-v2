from __future__ import annotations


TITLE_MAP = {
    "pharmacies": "💊 Дежурные аптеки",
    "electricity": "🔌 Отключения электричества",
    "water": "🚿 Отключения воды",
    "emergency": "🚨 Экстренные службы",
}


DETAILS_PREFIX_MAP = {
    "pharmacies": "🏥 ",
    "electricity": "⚠️ ",
    "water": "💧 ",
    "emergency": "ℹ️ ",
}


EMPTY_TEXT_MAP = {
    "pharmacies": "Сейчас данных по дежурным аптекам нет.",
    "electricity": "Плановых отключений электричества сейчас не найдено.",
    "water": "Плановых отключений воды сейчас не найдено.",
    "emergency": "Список экстренных служб пока пуст.",
}


def _category_key(category) -> str:
    return getattr(category, "value", str(category))


def render_feed_summary(feed) -> str:
    lines = ["События города", ""]

    updated_at = getattr(feed, "updated_at", "")
    if updated_at:
        lines.append(f"Обновлено: {updated_at}")
        lines.append("")

    items = getattr(feed, "items", []) or []
    if not items:
        lines.append("Нет данных.")
        return "\n".join(lines)

    for item in items:
        title = getattr(item, "title", "") or "—"
        count = getattr(item, "count", None)

        if count is None:
            lines.append(f"• {title}")
        else:
            lines.append(f"• {title} — {count}")

    return "\n".join(lines)


def render_category_payload(category, payload) -> str:
    category_key = _category_key(category)
    title = TITLE_MAP.get(category_key, "События города")
    details_prefix = DETAILS_PREFIX_MAP.get(category_key, "")
    empty_text = EMPTY_TEXT_MAP.get(category_key, "Сейчас данных нет.")

    if payload is None:
        return f"{title}\n\n{empty_text}"

    lines = [title, ""]

    updated_at = getattr(payload, "updated_at", "")
    if updated_at:
        lines.append(f"Обновлено: {updated_at}")
        lines.append("")

    items = getattr(payload, "items", []) or []
    if not items:
        lines.append(empty_text)
        return "\n".join(lines)

    total_items = len(items)

    for index, item in enumerate(items, start=1):
        title_value = getattr(item, "title", "") or "—"
        details = (getattr(item, "details", "") or "").strip()
        address = (getattr(item, "address", "") or "").strip()
        phone = (getattr(item, "phone", "") or "").strip()

        lines.append(f"{index}. {title_value}")

        if details:
            if details_prefix:
                detail_lines = details.splitlines()
                for detail_line in detail_lines:
                    detail_line = detail_line.strip()
                    if not detail_line:
                        continue
                    lines.append(f"{details_prefix}{detail_line}")
            else:
                lines.append(details)

        if address:
            lines.append(f"📍 {address}")

        if phone:
            lines.append(f"📞 {phone}")

        if index < total_items:
            lines.append("")
            lines.append("────────────")
            lines.append("")

    return "\n".join(lines)