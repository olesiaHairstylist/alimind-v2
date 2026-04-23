from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[3]

# PUBLIC слой
PUBLIC_DIR = BASE_DIR / "data" / "public" / "city_events"

FILES = {
    "electricity": "electricity_outages_today.json",
    "water": "water_outages_today.json",
    "pharmacies": "duty_pharmacies_today.json",
    "emergency": "emergency_contacts.json",
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_public_status() -> dict[str, str]:
    result: dict[str, str] = {}

    for key, filename in FILES.items():
        path = PUBLIC_DIR / filename
        data = _read_json(path)

        if not data:
            result[key] = "error"
            continue

        status = data.get("status")

        if status in ("ok", "empty", "error", "expected_empty"):
            result[key] = status
        else:
            result[key] = "error"

    return result


if __name__ == "__main__":
    print(read_public_status())