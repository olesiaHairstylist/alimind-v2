from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.modules.city_events.contracts.categories import CityEventCategory
from app.modules.city_events.parsers.water_cards import parse_water_items_from_html
from app.modules.city_events.storage.schema import CityEventPayload
from app.modules.city_events.storage.writer import write_payload

ASAT_URL = "https://kesinti.asat.gov.tr/dbo_kesintiListe/list"
TZ = ZoneInfo("Europe/Istanbul")


def _now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def build_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_html() -> str:
    session = build_session()
    r = session.get(
        ASAT_URL,
        timeout=(30, 60),
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    r.raise_for_status()
    return r.text


def fetch_payload() -> CityEventPayload:
    html = fetch_html()
    items = parse_water_items_from_html(html)

    return CityEventPayload(
        category=CityEventCategory.WATER,
        updated_at=_now_iso(),
        items=items,
    )


def run_and_save(data_dir: Path) -> Path:
    payload = fetch_payload()
    return write_payload(data_dir, payload)


if __name__ == "__main__":
    app_dir = Path(__file__).resolve().parents[3]
    data_dir = app_dir / "data" / "city_events"

    path = run_and_save(data_dir)
    print("WRITTEN:", path)
    print("ABS:", path.resolve())