from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.modules import fetch_pharmacies_raw_by_region
from app.modules import adapt_pharmacies_raw


OUTPUT_FILE = Path("app/data/sources/pharmacies_snapshot.json")


def build_pharmacies_snapshot(region_ids: Iterable[str]) -> list[dict[str, str]]:
    all_items: list[dict[str, str]] = []

    for region_id in region_ids:
        raw = fetch_pharmacies_raw_by_region(str(region_id))
        adapted = adapt_pharmacies_raw(raw, source_region_id=str(region_id))
        all_items.extend(adapted)

    return all_items


def write_pharmacies_snapshot(region_ids: Iterable[str]) -> Path:
    items = build_pharmacies_snapshot(region_ids)

    payload = {
        "type": "pharmacies_directory_snapshot",
        "source": "https://www.alanyaeo.org.tr/tr/eczane/getir",
        "region_ids": [str(x) for x in region_ids],
        "count": len(items),
        "items": items,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return OUTPUT_FILE