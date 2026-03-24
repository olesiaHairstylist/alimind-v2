from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "water_raw.json"
OUT_FILE = APP_DIR / "data" / "city_events" / "water_outages.json"


def load_raw() -> list[dict]:
    if not RAW_FILE.exists():
        return []

    text = RAW_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []

    data = json.loads(text)
    return data if isinstance(data, list) else []


def parse_water_items(data: list[dict]) -> list[dict]:
    items: list[dict] = []
    today = datetime.now().date()

    for row in data:
        if not isinstance(row, dict):
            continue

        title = str(row.get("title", "")).strip()
        area = str(row.get("area", "")).strip()
        start = str(row.get("start_at", "")).strip()
        end = str(row.get("end_at", "")).strip()
        note = str(row.get("note", "")).strip()
        address = str(row.get("address", "")).strip()

        if not title and not area:
            continue

        if start:
            try:
                start_date = datetime.strptime(start[:10], "%Y-%m-%d").date()
            except Exception:
                start_date = None
        else:
            start_date = None

        # временно без фильтра по дате
        # if start_date and start_date != today:
        #     continue

        period = f"{start} - {end}" if start and end else (start or end)

        display_title = title or area or "Отключение воды"

        details_lines: list[str] = []
        if period:
            details_lines.append(f"⏱ {period}")
        if note:
            details_lines.append(f"📌 {note}")

        items.append(
            {
                "title": display_title,
                "details": "\n".join(details_lines),
                "address": address,
                "phone": "",
            }
        )

    return items


def build_payload(items: list[dict]) -> dict:
    now_iso = datetime.now().isoformat()
    return {
        "category": "water",
        "updated_at": now_iso,
        "items": items,
    }


def save_payload(payload: dict) -> Path:
    print("SAVE PAYLOAD:", payload)
    print("OUT_FILE:", OUT_FILE)
    OUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return OUT_FILE


def run_build() -> Path:
    raw = load_raw()
    print("RAW COUNT:", len(raw))
    items = parse_water_items(raw)
    print("PARSED ITEMS:", items)
    payload = build_payload(items)
    return save_payload(payload)


if __name__ == "__main__":
    path = run_build()
    print("WRITTEN:", path)
    print("ABS:", path.resolve())