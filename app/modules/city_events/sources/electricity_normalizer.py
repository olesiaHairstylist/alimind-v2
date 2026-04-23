from __future__ import annotations

from datetime import datetime
from typing import Any


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split()).strip()


def _pick(raw: dict, *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if value is not None and str(value).strip():
            return _clean(value)
    return ""


def _format_time(raw: str) -> str:
    raw = _clean(raw)
    if not raw:
        return ""

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            if "%H" in fmt:
                return dt.strftime("%H:%M")
            return dt.strftime("%d.%m")
        except ValueError:
            pass

    return raw


def _build_details(raw: dict) -> str:
    start_raw = _pick(raw, "start_date", "startDate", "baslangic", "from", "date_start")
    end_raw = _pick(raw, "end_date", "endDate", "bitis", "to", "date_end")
    reason = _pick(raw, "reason", "type", "description", "aciklama", "work_type")

    lines: list[str] = []

    start_fmt = _format_time(start_raw)
    end_fmt = _format_time(end_raw)

    if start_fmt or end_fmt:
        if start_fmt and end_fmt:
            lines.append(f"⏱ {start_fmt} - {end_fmt}")
        elif start_fmt:
            lines.append(f"⏱ {start_fmt}")
        else:
            lines.append(f"⏱ {end_fmt}")

    if reason:
        lines.append(f"📌 {reason}")

    return "\n".join(lines).strip()


def normalize(raw_items: list[dict]) -> list[dict]:
    """
    Приводит сырые записи к стабильному контракту:
    title / details / address / phone
    """
    result: list[dict] = []

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue

        title = _pick(
            raw,
            "title",
            "name",
            "region",
            "area",
            "district",
            "mahalle",
            "location",
        )

        details = _build_details(raw)
        address = _pick(raw, "address", "adres")
        phone = _pick(raw, "phone", "telefon")

        item = {
            "title": title,
            "details": details,
            "address": address,
            "phone": phone,
        }

        # Отсеиваем совсем пустой мусор
        if any(item.values()):
            result.append(item)

    return result