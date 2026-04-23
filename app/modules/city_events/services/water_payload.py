from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")


def now_tr_iso() -> str:
    return datetime.now(ISTANBUL_TZ).isoformat()


def extract_raw_items(raw: list[dict]) -> list[dict]:
    items = []

    for row in raw:
        title = row.get("title") or row.get("region") or "Без названия"

        start = row.get("start_at") or row.get("start")
        end = row.get("end_at") or row.get("end")

        note = row.get("note") or row.get("reason") or ""

        items.append({
            "title": title,
            "start_at": start,
            "end_at": end,
            "note": note,
            "address": "",
            "phone": "",
        })

    return items


def build_water_payload(raw: list[dict]) -> dict:
    items = extract_raw_items(raw)

    return {
        "category": "water",
        "updated_at": now_tr_iso(),
        "status": "ok" if items else "empty",
        "items": items,
    }