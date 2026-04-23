from __future__ import annotations

import requests

from app.modules import ELECTRICITY_SOURCE_URL
from pathlib import Path
APP_DIR = Path(__file__).resolve().parents[3]

BASE_PATH = APP_DIR / "data" / "system" / "health"
BASE_PATH.mkdir(parents=True, exist_ok=True)

HEALTH_FILE = BASE_PATH / "city_events_health.json"
RAW_FILE = BASE_PATH / "electricity_raw.json"


def fetch_electricity_raw() -> str:
    payload = {
        "countryName": "ANTALYA",
        "cityName": "ALANYA",
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    response = requests.post(
        ELECTRICITY_SOURCE_URL,
        data=payload,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    return response.text


def save_electricity_raw(raw_text: str) -> Path:
    RAW_FILE.write_text(raw_text, encoding="utf-8")
    return RAW_FILE


def run_electricity_fetch() -> Path:
    raw_text = fetch_electricity_raw()
    return save_electricity_raw(raw_text)


if __name__ == "__main__":
    path = run_electricity_fetch()
    print("WRITTEN:", path)
    print("ABS:", path.resolve())