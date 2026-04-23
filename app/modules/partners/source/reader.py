from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
TRAVEL_PARTNERS_DIR = BASE_DIR / "data" / "partners" / "travel"


def load_raw_partner_files() -> list[dict[str, Any]]:
    if not TRAVEL_PARTNERS_DIR.exists():
        return []

    raw_items: list[dict[str, Any]] = []

    for path in sorted(TRAVEL_PARTNERS_DIR.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not isinstance(payload, dict):
            continue

        raw_items.append(payload)

    return raw_items

