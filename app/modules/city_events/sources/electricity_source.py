from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from app.modules.city_events.sources.electricity_extractor import (
    extract_outage_blocks_from_html,
    filter_alanya_blocks,
)

BASE_DIR = Path(__file__).resolve().parents[3]
RAW_PATH = BASE_DIR / "data" / "sources" / "electricity_raw.json"

PRIMARY_URL = "https://www.akdenizedas.com.tr/kesinti-liste"
FALLBACK_URL = "https://www.akdenizedas.com.tr/elektrik-kesintisi-sorgulama?il=ANTALYA&ilce=ALANYA"

TIMEOUT = 25

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass(slots=True)
class ElectricityFetchResult:
    status: str
    source_url: str
    items: list[dict[str, Any]]
    fetched_at: str
    error: str | None = None


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_raw(payload: dict[str, Any]) -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def fetch_electricity_raw() -> ElectricityFetchResult:
    fetched_at = _now_iso()

    for url in (PRIMARY_URL, FALLBACK_URL):
        try:
            html = _fetch_html(url)
            blocks = extract_outage_blocks_from_html(html)
            alanya_blocks = filter_alanya_blocks(blocks)

            if alanya_blocks:
                return ElectricityFetchResult(
                    status="ok",
                    source_url=url,
                    items=alanya_blocks,
                    fetched_at=fetched_at,
                    error=None,
                )

            # HTML доступен, но полезных ALANYA блоков не нашли
            return ElectricityFetchResult(
                status="empty",
                source_url=url,
                items=[],
                fetched_at=fetched_at,
                error=None,
            )

        except requests.RequestException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"

    return ElectricityFetchResult(
        status="error",
        source_url=PRIMARY_URL,
        items=[],
        fetched_at=fetched_at,
        error=last_error,
    )


def run_fetch() -> dict[str, Any]:
    """
    Пишет RAW snapshot для следующего слоя.
    Ничего не нормализует под UI.
    """
    result = fetch_electricity_raw()

    payload: dict[str, Any] = {
        "category": "electricity",
        "source": "aedas_html_v2",
        "source_url": result.source_url,
        "fetched_at": result.fetched_at,
        "status": result.status,
        "items": result.items,
    }

    if result.error:
        payload["error"] = result.error

    _write_raw(payload)
    return payload


if __name__ == "__main__":
    data = run_fetch()
    print(f"STATUS: {data.get('status')}")
    print(f"ITEMS: {len(data.get('items', []))}")
    print(f"RAW SAVED: {RAW_PATH}")