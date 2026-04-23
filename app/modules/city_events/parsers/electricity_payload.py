from __future__ import annotations

import re
from typing import Any


def extract_raw_items(raw_data: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw_data, dict):
        return []

    items = raw_data.get("items")
    if not isinstance(items, list):
        return []

    return [item for item in items if isinstance(item, dict)]


def _is_valid_electricity_item(item: dict[str, Any]) -> bool:
    title = str(item.get("title", "")).strip()
    start_at = str(item.get("start_at", "")).strip()
    end_at = str(item.get("end_at", "")).strip()

    if not title:
        return False

    compact = title.replace(" ", "")
    if compact in {"—", "——", "———", "---", "----", "-----"}:
        return False

    parts = title.split(".")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        return False

    if title.lower() == "сегодня":
        return False

    if not (start_at or end_at):
        return False

    return True


def _extract_group_date(item: dict[str, Any]) -> str:
    start_at = str(item.get("start_at", "")).strip()
    if start_at and len(start_at) >= 10:
        return start_at[:10]
    return "Без даты"


def _group_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for item in items:
        date_key = _extract_group_date(item)
        grouped.setdefault(date_key, []).append(item)

    result: list[dict[str, Any]] = []
    for date_key, group_items in grouped.items():
        result.append(
            {
                "date": date_key,
                "items": group_items,
            }
        )

    return result


def _clean_geo_token(token: str) -> str:
    token = token.strip()
    if not token:
        return ""

    token = re.sub(r"\bANTALYA\b", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\bALANYA\b", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\bMERKEZ\b", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\bMah\.?\b", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\bCd\.?\b", "", token, flags=re.IGNORECASE)
    token = re.sub(r"\bSk\.?\b", "", token, flags=re.IGNORECASE)

    token = re.sub(r"\s+", " ", token).strip(" ,-/")
    return token


def _normalize_electricity_title(raw_title: str) -> str:
    raw_title = (raw_title or "").strip()
    if not raw_title:
        return ""

    parts = [part.strip() for part in raw_title.split(",")]
    cleaned_parts: list[str] = []

    for part in parts:
        cleaned = _clean_geo_token(part)

        if not cleaned:
            continue

        upper = cleaned.upper()
        if upper in {"ANTALYA", "ALANYA", "MERKEZ"}:
            continue

        if cleaned not in cleaned_parts:
            cleaned_parts.append(cleaned)

    # Берём первые 3 осмысленных куска
    cleaned_parts = cleaned_parts[:3]

    if not cleaned_parts:
        return raw_title

    return " / ".join(cleaned_parts)


def build_electricity_payload(
    raw_items: list[dict[str, Any]],
    updated_at: str | None = None,
) -> dict[str, Any]:
    result_items: list[dict[str, Any]] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        raw_title = str(item.get("title", "")).strip()

        public_item = {
            "title": _normalize_electricity_title(raw_title),
            "start_at": str(item.get("start_at", "")).strip(),
            "end_at": str(item.get("end_at", "")).strip(),
            "note": str(item.get("note", "")).strip(),
            "address": str(item.get("address", "")).strip(),
            "phone": str(item.get("phone", "")).strip(),
        }

        if not _is_valid_electricity_item(public_item):
            continue

        result_items.append(public_item)

    status = "ok" if result_items else "empty"
    groups = _group_items(result_items) if result_items else []
    print("DEBUG TITLE:", raw_title, "->", _normalize_electricity_title(raw_title))
    return {
        "category": "electricity",
        "updated_at": updated_at,
        "status": status,
        "items": result_items,
        "groups": groups,
    }
