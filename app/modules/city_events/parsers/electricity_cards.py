from __future__ import annotations

import re
from datetime import datetime
from typing import Any


AREA_RE = re.compile(
    r"(?:ANTALYA\s*/\s*ALANYA\s*/\s*)(.+?)(?:\s*-\s*|\s*$)",
    re.IGNORECASE,
)


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


def parse_iso_dt(value: Any) -> datetime | None:
    raw = normalize_text(value)
    if not raw:
        return None

    candidates = [
        raw,
        raw.replace("Z", "+00:00"),
    ]

    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass

    return None


def _extract_area_from_message(message: str) -> str:
    text = normalize_text(message)
    if not text:
        return ""

    match = AREA_RE.search(text)
    if match:
        return normalize_text(match.group(1))

    return ""


def _extract_reason(item: dict) -> str:
    candidates = [
        item.get("reason"),
        item.get("reasonName"),
        item.get("outageReason"),
        item.get("type"),
        item.get("typeName"),
        item.get("notificationType"),
    ]

    for value in candidates:
        text = normalize_text(value)
        if text:
            return text

    return ""


def _extract_message(item: dict) -> str:
    candidates = [
        item.get("message"),
        item.get("description"),
        item.get("text"),
        item.get("detail"),
        item.get("details"),
    ]

    for value in candidates:
        text = normalize_text(value)
        if text:
            return text

    return ""


def _extract_title(item: dict, message: str) -> str:
    candidates = [
        item.get("area"),
        item.get("areaName"),
        item.get("region"),
        item.get("regionName"),
        item.get("location"),
        item.get("title"),
    ]

    for value in candidates:
        text = normalize_text(value)
        if text:
            return text

    area_from_message = _extract_area_from_message(message)
    if area_from_message:
        return area_from_message

    return "Без названия"


def _extract_address(item: dict) -> str:
    candidates = [
        item.get("address"),
        item.get("fullAddress"),
        item.get("locationText"),
    ]

    for value in candidates:
        text = normalize_text(value)
        if text:
            return text

    return ""


def _extract_phone(item: dict) -> str:
    candidates = [
        item.get("phone"),
        item.get("contactPhone"),
    ]

    for value in candidates:
        text = normalize_text(value)
        if text:
            return text

    return ""


def _is_alanya_record(item: dict, message: str) -> bool:
    joined = " | ".join(
        [
            normalize_text(item.get("city")),
            normalize_text(item.get("district")),
            normalize_text(item.get("region")),
            normalize_text(item.get("area")),
            normalize_text(message),
        ]
    ).upper()

    return "ALANYA" in joined


def _extract_start_end(item: dict) -> tuple[str, str]:
    start_candidates = [
        item.get("start_at"),
        item.get("startDateTime"),
        item.get("startDate"),
        item.get("plannedStartDate"),
        item.get("beginDate"),
    ]
    end_candidates = [
        item.get("end_at"),
        item.get("endDateTime"),
        item.get("endDate"),
        item.get("plannedEndDate"),
        item.get("finishDate"),
    ]

    start_dt = None
    end_dt = None

    for value in start_candidates:
        start_dt = parse_iso_dt(value)
        if start_dt:
            break

    for value in end_candidates:
        end_dt = parse_iso_dt(value)
        if end_dt:
            break

    start_str = start_dt.isoformat() if start_dt else ""
    end_str = end_dt.isoformat() if end_dt else ""

    return start_str, end_str


def build_electricity_cards(raw_items: list[dict]) -> list[dict]:
    cards: list[dict] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        message = _extract_message(item)

        if not _is_alanya_record(item, message):
            continue

        start_at, end_at = _extract_start_end(item)
        if not start_at:
            continue

        title = _extract_title(item, message)
        note = _extract_reason(item)
        address = _extract_address(item)
        phone = _extract_phone(item)

        card = {
            "title": title,
            "start_at": start_at,
            "end_at": end_at,
            "note": note,
            "address": address,
            "phone": phone,
        }
        cards.append(card)

    cards.sort(key=lambda x: x.get("start_at", ""))
    return cards


def parse_electricity_items_from_raw(raw_items: list[dict]) -> list[dict]:
    return build_electricity_cards(raw_items)