from __future__ import annotations

import re
from datetime import datetime
from typing import Any


MAX_ITEMS = 15

TITLE_MAP = {
    "ru": {
        "pharmacies": "💊 Дежурные аптеки",
        "electricity": "⚡ Отключения электричества",
        "water": "💧 Отключения воды",
        "emergency": "☎️ Экстренные службы",
    },
    "en": {
        "pharmacies": "💊 Duty Pharmacies",
        "electricity": "⚡ Electricity Outages",
        "water": "💧 Water Outages",
        "emergency": "☎️ Emergency Contacts",
    },
    "tr": {
        "pharmacies": "💊 Nobetci Eczaneler",
        "electricity": "⚡ Elektrik Kesintileri",
        "water": "💧 Su Kesintileri",
        "emergency": "☎️ Acil Hizmetler",
    },
}

UPDATED_AT_LABEL = {
    "ru": "Обновлено",
    "en": "Updated",
    "tr": "Guncellendi",
}

NO_DATA_TEXT = {
    "ru": "Сегодня данных нет.",
    "en": "No data for today.",
    "tr": "Bugun veri yok.",
}

BROKEN_DATA_TEXT = {
    "ru": "Источник временно недоступен.",
    "en": "Source is temporarily unavailable.",
    "tr": "Kaynak gecici olarak kullanilamiyor.",
}

NO_NAME_TEXT = {
    "ru": "Без названия",
    "en": "Untitled",
    "tr": "Adsiz",
}

NO_DATE_TEXT = {
    "ru": "Без даты",
    "en": "No date",
    "tr": "Tarih yok",
}

TODAY_TEXT = {
    "ru": "Сегодня",
    "en": "Today",
    "tr": "Bugun",
}

PHARMACIES_EMPTY_TEXT = {
    "ru": "Сегодня дежурные аптеки не найдены.",
    "en": "No duty pharmacies found today.",
    "tr": "Bugun nobetci eczane bulunamadi.",
}

ELECTRICITY_EMPTY_TEXT = {
    "ru": "Сегодня отключений электричества не запланировано.",
    "en": "No electricity outages scheduled for today.",
    "tr": "Bugun elektrik kesintisi planlanmamis.",
}

WATER_EMPTY_TEXT = {
    "ru": "Сегодня отключений воды не запланировано.",
    "en": "No water outages scheduled for today.",
    "tr": "Bugun su kesintisi planlanmamis.",
}

EMERGENCY_EMPTY_TEXT = {
    "ru": "Сегодня данных нет.",
    "en": "No data for today.",
    "tr": "Bugun veri yok.",
}

LIMIT_NOTE_TEXT = {
    "ru": "\n\nПоказаны первые {count} записей.",
    "en": "\n\nShowing first {count} records.",
    "tr": "\n\nIlk {count} kayit gosteriliyor.",
}

DETAILS_PREFIX_MAP = {
    "ru": {
        "pharmacies": "🏥 ",
        "electricity": "⚠️ ",
        "water": "💧 ",
        "emergency": "ℹ️ ",
    },
    "en": {
        "pharmacies": "🏥 ",
        "electricity": "⚠️ ",
        "water": "💧 ",
        "emergency": "ℹ️ ",
    },
    "tr": {
        "pharmacies": "🏥 ",
        "electricity": "⚠️ ",
        "water": "💧 ",
        "emergency": "ℹ️ ",
    },
}

DIVIDER = "\n\n— — —\n\n"

DETAILS_TIME_RE = re.compile(
    r"⏱\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})"
)
DETAILS_NOTE_RE = re.compile(r"📌\s*(.+)")


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _collapse_spaces(text: str) -> str:
    return " ".join(text.split()).strip()


def normalize_text(text: Any) -> str:
    text = _safe_str(text)
    text = text.replace("\r", " ").replace("\n", " ")
    return _collapse_spaces(text)


def trim_address(text: str, max_len: int = 70) -> str:
    text = normalize_text(text)
    if not text:
        return ""

    if len(text) <= max_len:
        return text

    cut = text[:max_len].rstrip(" ,.-")
    return cut + "..."


def format_datetime_short(value: str | None) -> str:
    raw = normalize_text(value)
    if not raw:
        return ""

    candidates = [raw, raw.replace("Z", "+00:00")]

    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
            return dt.strftime("%d.%m %H:%M")
        except ValueError:
            pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%d.%m %H:%M") if "H" in fmt else dt.strftime("%d.%m")
        except ValueError:
            pass

    return raw


def _parse_date(date_str: str) -> datetime | None:
    raw = normalize_text(date_str)
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def format_date_label(date_str: str, lang: str = "ru") -> str:
    dt = _parse_date(date_str)
    if dt is None:
        return date_str or NO_DATE_TEXT.get(lang, NO_DATE_TEXT["ru"])

    today = datetime.now().date()
    if dt.date() == today:
        return TODAY_TEXT.get(lang, TODAY_TEXT["ru"])

    return dt.strftime("%d.%m.%Y")


def _build_header(title: str, updated_at: str | None = None, lang: str = "ru") -> str:
    lines = [title]

    updated = format_datetime_short(updated_at)
    if updated:
        lines.append(f"{UPDATED_AT_LABEL.get(lang, UPDATED_AT_LABEL['ru'])}: {updated}")

    lines.append("")
    return "\n".join(lines)


def _limit_items(items: list[dict], lang: str = "ru") -> tuple[list[dict], str]:
    if len(items) <= MAX_ITEMS:
        return items, ""

    limited = items[:MAX_ITEMS]
    note = LIMIT_NOTE_TEXT.get(lang, LIMIT_NOTE_TEXT["ru"]).format(count=MAX_ITEMS)
    return limited, note


def render_pharmacies(payload: dict, lang: str = "ru") -> str:
    title = TITLE_MAP.get(lang, TITLE_MAP["ru"])["pharmacies"]
    if not isinstance(payload, dict):
        return f"{title}\n\n{BROKEN_DATA_TEXT.get(lang, BROKEN_DATA_TEXT['ru'])}"

    updated_at = payload.get("updated_at")
    items = payload.get("items") or []
    header = _build_header(title, updated_at, lang)

    if not items:
        return header + PHARMACIES_EMPTY_TEXT.get(lang, PHARMACIES_EMPTY_TEXT["ru"])

    items, limit_note = _limit_items(items, lang)
    blocks: list[str] = []
    for idx, item in enumerate(items, start=1):
        title_value = normalize_text(item.get("title") or item.get("name") or NO_NAME_TEXT.get(lang, NO_NAME_TEXT["ru"]))
        address = trim_address(item.get("address", ""))
        phone = normalize_text(item.get("phone", ""))

        lines = [f"{idx}) {title_value}", ""]

        if address:
            lines.append(f"📍 {address}")
            lines.append("")

        if phone:
            lines.append(f"☎ {phone}")

        blocks.append("\n".join(lines))

    return header + DIVIDER.join(blocks) + limit_note


def _parse_details_block(details: str) -> dict[str, str]:
    raw = _safe_str(details)
    if not raw:
        return {"date": "", "time_range": "", "note": ""}

    date_value = ""
    time_range = ""
    note = ""

    time_match = DETAILS_TIME_RE.search(raw)
    if time_match:
        start_date, start_time, end_date, end_time = time_match.groups()
        date_value = start_date
        time_range = f"{start_time[:5]} — {end_time[:5]}"
        if start_date != end_date:
            time_range = f"{start_date} {start_time[:5]} — {end_date} {end_time[:5]}"

    note_match = DETAILS_NOTE_RE.search(raw)
    if note_match:
        note = normalize_text(note_match.group(1))

    return {"date": date_value, "time_range": time_range, "note": note}


def _group_outages_from_v1(items: list[dict], lang: str = "ru") -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = {}

    for item in items:
        parsed = _parse_details_block(_safe_str(item.get("details", "")))
        date_key = parsed["date"] or NO_DATE_TEXT.get(lang, NO_DATE_TEXT["ru"])

        prepared = {
            "title": normalize_text(item.get("title") or NO_NAME_TEXT.get(lang, NO_NAME_TEXT["ru"])),
            "time_range": parsed["time_range"],
            "note": parsed["note"],
            "address": trim_address(item.get("address", ""), max_len=90),
            "phone": normalize_text(item.get("phone", "")),
            "date": date_key,
        }
        grouped.setdefault(date_key, []).append(prepared)

    no_date = NO_DATE_TEXT.get(lang, NO_DATE_TEXT["ru"])

    def sort_group_key(group_key: str) -> tuple[int, str]:
        if group_key == no_date:
            return (1, group_key)
        return (0, group_key)

    return [(group_key, grouped[group_key]) for group_key in sorted(grouped.keys(), key=sort_group_key)]


def render_outages(
    payload: dict,
    *,
    title: str,
    empty_text: str,
    lang: str = "ru",
) -> str:
    if not isinstance(payload, dict):
        return f"{title}\n\n{BROKEN_DATA_TEXT.get(lang, BROKEN_DATA_TEXT['ru'])}"

    updated_at = payload.get("updated_at")
    items = payload.get("items") or []
    header = _build_header(title, updated_at, lang)

    if not items:
        return header + empty_text

    items, limit_note = _limit_items(items, lang)
    grouped = _group_outages_from_v1(items, lang)

    chunks: list[str] = []
    counter = 1

    for date_key, date_items in grouped:
        date_label = format_date_label(date_key, lang)
        chunks.append(f"📅 {date_label}\n")

        group_blocks: list[str] = []
        for item in date_items:
            lines = [f"{counter}. {item['title']}"]

            if item["time_range"]:
                lines.append(f"⏱ {item['time_range']}")

            if item["note"]:
                lines.append(f"⚠️ {item['note']}")

            if item["address"]:
                lines.append(f"📍 {item['address']}")

            if item["phone"]:
                lines.append(f"📞 {item['phone']}")

            group_blocks.append("\n".join(lines))
            counter += 1

        chunks.append(DIVIDER.join(group_blocks))

    return header + "\n\n".join(chunks) + limit_note


def render_water(payload: dict, lang: str = "ru") -> str:
    title = TITLE_MAP.get(lang, TITLE_MAP["ru"])["water"]
    if not isinstance(payload, dict):
        return f"{title}\n\n{BROKEN_DATA_TEXT.get(lang, BROKEN_DATA_TEXT['ru'])}"

    return render_outages(
        payload,
        title=title,
        empty_text=WATER_EMPTY_TEXT.get(lang, WATER_EMPTY_TEXT["ru"]),
        lang=lang,
    )


def render_emergency(payload: dict, lang: str = "ru") -> str:
    title = TITLE_MAP.get(lang, TITLE_MAP["ru"])["emergency"]
    if not isinstance(payload, dict):
        return f"{title}\n\n{BROKEN_DATA_TEXT.get(lang, BROKEN_DATA_TEXT['ru'])}"

    items = payload.get("items") or []
    header = _build_header(title, payload.get("updated_at"), lang)

    if not items:
        return header + EMERGENCY_EMPTY_TEXT.get(lang, EMERGENCY_EMPTY_TEXT["ru"])

    items, limit_note = _limit_items(items, lang)
    lines: list[str] = []
    for item in items:
        title_value = normalize_text(item.get("title") or item.get("name") or NO_NAME_TEXT.get(lang, NO_NAME_TEXT["ru"]))
        phone = normalize_text(item.get("phone", ""))
        details = normalize_text(item.get("details", ""))

        row = f"• {title_value}"
        if phone:
            row += f" — {phone}"
        lines.append(row)

        if details:
            lines.append(f"  {details}")

    return header + "\n".join(lines) + limit_note


def render_category_payload(category: str, payload: dict, lang: str = "ru") -> str:
    category_key = normalize_text(category).lower()

    if category_key in {"pharmacies", "duty_pharmacy", "duty_pharmacies"}:
        return render_pharmacies(payload, lang=lang)

    if category_key in {"electricity", "electricity_outage", "electricity_outages"}:
        return render_outages(
            payload,
            title=TITLE_MAP.get(lang, TITLE_MAP["ru"])["electricity"],
            empty_text=ELECTRICITY_EMPTY_TEXT.get(lang, ELECTRICITY_EMPTY_TEXT["ru"]),
            lang=lang,
        )

    if category_key in {"water", "water_outage", "water_outages"}:
        return render_water(payload, lang=lang)

    if category_key in {"emergency", "emergency_contact", "emergency_contacts"}:
        return render_emergency(payload, lang=lang)

    return BROKEN_DATA_TEXT.get(lang, BROKEN_DATA_TEXT["ru"])
