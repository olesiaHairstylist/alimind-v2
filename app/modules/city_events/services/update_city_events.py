from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.modules.city_events.sources.electricity_source import fetch_raw_data
from app.modules.city_events.parsers.electricity_cards import (
    parse_electricity_items_from_raw,
)
from app.modules.city_events.sources.asat_water_adapter import run_and_save as run_water_update


TZ = ZoneInfo("Europe/Istanbul")
APP_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = APP_DIR / "data" / "city_events"
ELECTRICITY_FILE = DATA_DIR / "electricity_outages.json"


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, payload: dict) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    tmp_path.replace(path)


def update_electricity() -> None:
    raw = fetch_raw_data()
    print(f"[FETCH] electricity raw: {len(raw)}")

    items = parse_electricity_items_from_raw(raw)

    payload = {
        "category": "electricity",
        "updated_at": now_iso(),
        "items": items,
    }

    atomic_write_json(ELECTRICITY_FILE, payload)
    print(f"[OK] electricity updated -> {ELECTRICITY_FILE} (items={len(items)})")


def update_water() -> None:
    path = run_water_update(DATA_DIR)
    print(f"[OK] water updated -> {path}")


def main() -> int:
    ensure_data_dir()
    errors: list[str] = []

    print("CITY_EVENTS_UPDATE_START")

    try:
        update_electricity()
    except Exception as e:
        errors.append(f"electricity: {e}")
        print(f"[ERROR] electricity failed: {e}")

    try:
        update_water()
    except Exception as e:
        errors.append(f"water: {e}")
        print(f"[ERROR] water failed: {e}")

    print("CITY_EVENTS_UPDATE_END")

    if errors:
        print("SUMMARY: PARTIAL_OR_FAILED")
        for err in errors:
            print(f" - {err}")
        return 0

    print("SUMMARY: SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())