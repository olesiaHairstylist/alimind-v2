from __future__ import annotations

from typing import Any


TITLE = "🩺 Состояние CITY EVENTS"


STATUS_LABELS = {
    "ok": "✅ OK",
    "empty": "🟡 EMPTY",
    "expected_empty": "🟡 EXPECTED EMPTY",
    "error": "🔴 ERROR",
}

FRESHNESS_LABELS = {
    "fresh": "🟢 fresh",
    "aging": "🟠 aging",
    "stale": "🔴 stale",
    "unknown": "⚪ unknown",
}

CATEGORY_LABELS = {
    "electricity": "⚡ Электричество",
    "water": "🚰 Вода",
    "pharmacies": "💊 Аптеки",
    "emergency": "🚨 Экстренные",
}


def _line(label: str, value: str) -> str:
    return f"{label}: {value}"


def render_health_snapshot(snapshot: dict[str, Any] | None) -> str:
    if not snapshot or not isinstance(snapshot, dict):
        return f"{TITLE}\n\nНет health snapshot."

    updated_at = snapshot.get("updated_at", "unknown")
    sources = snapshot.get("sources") or {}

    lines: list[str] = [
        TITLE,
        "",
        f"Обновлено: {updated_at}",
        "",
    ]

    for key in ("electricity", "water", "pharmacies", "emergency"):
        entry = sources.get(key)
        label = CATEGORY_LABELS.get(key, key)

        lines.append(label)

        if not isinstance(entry, dict):
            raw_status = str(entry) if entry is not None else "unknown"
            lines.append(_line("Статус", STATUS_LABELS.get(raw_status, raw_status)))
            lines.append("")
            continue

        status = entry.get("status", "unknown")
        items_count = entry.get("items_count", 0)
        freshness = entry.get("freshness", "unknown")
        is_expected_empty = entry.get("is_expected_empty", False)
        source_updated_at = entry.get("updated_at", "unknown")
        error_details = entry.get("error_details")

        lines.append(_line("Статус", STATUS_LABELS.get(status, status)))
        lines.append(_line("Элементов", str(items_count)))
        lines.append(_line("Свежесть", FRESHNESS_LABELS.get(freshness, freshness)))
        lines.append(_line("Источник обновлён", str(source_updated_at)))
        lines.append(_line("Ожидаемая пустота", "да" if is_expected_empty else "нет"))

        if error_details:
            lines.append(_line("Детали", str(error_details)))

        lines.append("")

    return "\n".join(lines).strip()