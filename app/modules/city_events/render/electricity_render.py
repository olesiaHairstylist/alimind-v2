from __future__ import annotations

from typing import Any


TITLE_MAP = {
    "ru": "⚡ Плановые отключения электричества",
    "en": "⚡ Scheduled Electricity Outages",
    "tr": "⚡ Planli Elektrik Kesintileri",
}

NO_DATA_MAP = {
    "ru": "Нет данных",
    "en": "No data",
    "tr": "Veri yok",
}

EMPTY_MAP = {
    "ru": "Сегодня данных нет",
    "en": "No data for today",
    "tr": "Bugun veri yok",
}

FROM_MAP = {
    "ru": "С",
    "en": "From",
    "tr": "Baslangic",
}

TO_MAP = {
    "ru": "До",
    "en": "Until",
    "tr": "Bitis",
}


def _short_time(value: str) -> str:
    value = (value or "").strip()
    if len(value) >= 16:
        return value[11:16]
    return value


def render_electricity(payload: dict[str, Any], lang: str = "ru") -> str:
    title = TITLE_MAP.get(lang, TITLE_MAP["ru"])
    if not payload:
        return f"{title}\n\n{NO_DATA_MAP.get(lang, NO_DATA_MAP['ru'])}"

    status = payload.get("status")
    groups = payload.get("groups") or []
    items = payload.get("items") or []

    if status == "empty":
        return f"{title}\n\n{EMPTY_MAP.get(lang, EMPTY_MAP['ru'])}"

    lines: list[str] = [title, ""]

    if groups:
        for group in groups:
            date_label = str(group.get("date", "")).strip()
            group_items = group.get("items") or []

            if date_label:
                lines.append(f"📅 {date_label}")
                lines.append("")

            for idx, item in enumerate(group_items, start=1):
                title_value = str(item.get("title", "")).strip()
                start_at = str(item.get("start_at", "")).strip()
                end_at = str(item.get("end_at", "")).strip()
                note = str(item.get("note", "")).strip()
                address = str(item.get("address", "")).strip()
                phone = str(item.get("phone", "")).strip()

                lines.append(f"{idx}. {title_value}")

                start_short = _short_time(start_at)
                end_short = _short_time(end_at)

                if start_short or end_short:
                    if start_short and end_short:
                        lines.append(f"🕒 {start_short} — {end_short}")
                    elif start_short:
                        lines.append(f"🕒 {FROM_MAP.get(lang, FROM_MAP['ru'])} {start_short}")
                    else:
                        lines.append(f"🕒 {TO_MAP.get(lang, TO_MAP['ru'])} {end_short}")

                if note:
                    lines.append(f"📌 {note}")

                if address:
                    lines.append(f"📍 {address}")

                if phone:
                    lines.append(f"📞 {phone}")

                lines.append("")

    else:
        for idx, item in enumerate(items, start=1):
            title_value = str(item.get("title", "")).strip()
            start_at = str(item.get("start_at", "")).strip()
            end_at = str(item.get("end_at", "")).strip()
            note = str(item.get("note", "")).strip()

            lines.append(f"{idx}. {title_value}")

            start_short = _short_time(start_at)
            end_short = _short_time(end_at)

            if start_short or end_short:
                if start_short and end_short:
                    lines.append(f"🕒 {start_short} — {end_short}")
                elif start_short:
                    lines.append(f"🕒 {FROM_MAP.get(lang, FROM_MAP['ru'])} {start_short}")
                else:
                    lines.append(f"🕒 {TO_MAP.get(lang, TO_MAP['ru'])} {end_short}")

            if note:
                lines.append(f"📌 {note}")

            lines.append("")

    return "\n".join(lines).strip()
