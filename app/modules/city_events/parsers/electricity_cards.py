from __future__ import annotations

from typing import Any


def _extract_area_from_message(message: str) -> str:
    area = "Alanya"

    if not message:
        return area

    parts = [p.strip() for p in message.split(",") if p.strip()]
    if len(parts) < 3:
        return area

    raw_area = parts[2]

    stop_markers = [
        " bölgelerinde",
        " saatleri arasında",
        " Sebebi ile",
    ]

    for marker in stop_markers:
        if marker in raw_area:
            raw_area = raw_area.split(marker)[0].strip()

    if "Mah." in raw_area:
        left, _, _ = raw_area.partition("Mah.")
        return f"{left.strip()} Mah."

    return raw_area.strip() or area


def parse_electricity_items_from_raw(data: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    for row in data:
        planned = row.get("plannedOutage") or {}
        if not isinstance(planned, dict):
            continue

        city = str(planned.get("city", "")).strip().upper()
        county = str(planned.get("county", "")).strip().upper()

        if city != "ANTALYA" or county != "ALANYA":
            continue

        start = str(planned.get("startDateTime", "")).strip()
        end = str(planned.get("endDateTime", "")).strip()
        reason = str(planned.get("reason", "")).strip()
        message = str(planned.get("message", "")).strip()

        if not start:
            continue

        period = f"{start} - {end}" if start and end else start
        area = _extract_area_from_message(message)

        items.append(
            {
                "title": area,
                "details": f"⏱ {period}\n📌 {reason or message}",
                "address": "",
                "phone": "",
            }
        )

    return items


def normalize_electricity_payload(payload: dict[str, Any]) -> list[dict[str, str]]:
    items = payload.get("items", [])
    if not isinstance(items, list):
        return []

    normalized: list[dict[str, str]] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        normalized.append(
            {
                "title": str(item.get("title", "")).strip(),
                "details": str(item.get("details", "")).strip(),
                "address": str(item.get("address", "")).strip(),
                "phone": str(item.get("phone", "")).strip(),
            }
        )

    return normalized