from __future__ import annotations

import json
from pathlib import Path

from app.modules.city_events.services.water_payload import build_water_payload

APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "water_raw.json"

PUBLIC_FILE = (
    APP_DIR
    / "data"
    / "public"
    / "city_events"
    / "water_outages_today.json"
)


def load_raw() -> list[dict]:
    if not RAW_FILE.exists():
        return []

    return json.loads(RAW_FILE.read_text(encoding="utf-8"))


def save_public(payload: dict) -> Path:
    PUBLIC_FILE.parent.mkdir(parents=True, exist_ok=True)

    PUBLIC_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return PUBLIC_FILE


def run_build() -> Path:
    raw = load_raw()

    payload = build_water_payload(raw)

    path = save_public(payload)

    print("PUBLIC BUILT:", path)
    print("ITEMS:", len(payload["items"]))
    print("STATUS:", payload["status"])

    return path


if __name__ == "__main__":
    run_build()