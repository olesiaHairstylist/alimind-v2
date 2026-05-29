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
DISTRICT_RU = {
    "CİKCİLLİ": "Джикджилли",
    "CUMHURİYET": "Джумхуриет",
    "ŞEKERHANE": "Шекерхане",
    "OBA": "Оба",
    "TOSMUR": "Тосмур",
    "MAHMUTLAR": "Махмутлар",
    "KARGICAK": "Каргыджак",
    "AVSALLAR": "Авсаллар",
    "PAYALLAR": "Паяллар",
    "TÜRKLER": "Тюрклер",
    "KONAKLI": "Конаклы",
}
def _find_district(title: str) -> str:
    upper = title.upper()

    for district in DISTRICT_RU:
        if district in upper:
            return district

    return ""
def _district_ru_name(district: str) -> str:
    return DISTRICT_RU.get(district, "")

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
                clean_title = (
                    title_value
                    .replace("ANTALYA,", "")
                    .replace("ALANYA,", "")
                    .replace("MERKEZ ", "")
                )
                location = clean_title.replace(",", "\n• ")

                lines.append(f"📍 {location}")

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

            clean_title = (
                title_value
                .replace("ANTALYA,", "")
                .replace("ALANYA,", "")
                .replace("MERKEZ ", "")
            )

            location = clean_title.replace(",", "\n• ")
            district = _find_district(clean_title)
            display_location = location

            if district:
                display_location = display_location.replace(district, "").strip()
                display_location = display_location.replace("• ", "• ")

            lines.append(f"📍 Район: {district}")

            if lang == "ru" and district:
                ru_name = _district_ru_name(district)
                if ru_name:
                    lines.append(f"({ru_name})")

            lines.append("")

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
                if note == "Bakım Çalışması":
                    note = "Техническое обслуживание"

                elif note == "Yatırım Çalışması":
                    note = "Плановые работы"

                elif note == "Güvenlik":
                    note = "Работы по безопасности"
                lines.append(f"🔧 {note}")

            lines.append("")

    return "\n".join(lines).strip()
