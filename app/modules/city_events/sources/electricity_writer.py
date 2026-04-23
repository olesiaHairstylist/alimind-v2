from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]  # до корня проекта
OUTPUT_PATH = BASE_DIR / "data/public/city_events/electricity_outages_today.json"


def save_electricity_payload(payload: dict) -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return OUTPUT_PATH