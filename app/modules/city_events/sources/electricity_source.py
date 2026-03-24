from __future__ import annotations

import json
from pathlib import Path

import requests


APP_DIR = Path(__file__).resolve().parents[3]

RAW_FILE = APP_DIR / "data" / "sources" / "electricity_raw.json"

URL = "https://www.akdenizedas.com.tr/elektrik-getir"


def fetch_raw_data() -> list[dict]:
    payload = {
        "countryName": "ANTALYA",
        "cityName": "ALANYA",
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    response = requests.post(URL, data=payload, headers=headers, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data if isinstance(data, list) else []


def save_raw(data: list[dict]) -> Path:
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)

    RAW_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return RAW_FILE


def run_fetch() -> Path:
    data = fetch_raw_data()
    print("FETCHED:", len(data))
    return save_raw(data)


if __name__ == "__main__":
    path = run_fetch()
    print("RAW SAVED:", path)