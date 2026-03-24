from __future__ import annotations

import json
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

APP_DIR = Path(__file__).resolve().parents[3]
RAW_FILE = APP_DIR / "data" / "sources" / "electricity_raw.json"

URL = "https://www.akdenizedas.com.tr/elektrik-getir"


def build_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["POST"]),
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_raw_data() -> list[dict]:
    payload = {
        "countryName": "ANTALYA",
        "cityName": "ALANYA",
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
    }

    session = build_session()
    response = session.post(URL, data=payload, headers=headers, timeout=(30, 60))
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