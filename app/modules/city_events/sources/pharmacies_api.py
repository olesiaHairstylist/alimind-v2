from __future__ import annotations

from typing import Any, Dict
import requests

BASE_URL = "https://www.alanyaeo.org.tr"
PHARMACIES_PAGE_URL = f"{BASE_URL}/tr/nobetci-eczaneler"
PHARMACIES_AJAX_URL = f"{BASE_URL}/tr/eczane/getir"

DEFAULT_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": PHARMACIES_PAGE_URL,
    "User-Agent": "Mozilla/5.0",
}


def fetch_pharmacies_raw_by_region(region_id: str, timeout: int = 20) -> Dict[str, Any]:
    response = requests.post(
        PHARMACIES_AJAX_URL,
        data={"bolgeId": str(region_id)},
        headers=DEFAULT_HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    return data if isinstance(data, dict) else {"data": []}