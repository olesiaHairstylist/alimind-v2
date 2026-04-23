from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[3]
HEALTH_PATH = BASE_DIR / "data" / "system" / "health" / "city_events_health.json"


def read_health_snapshot() -> dict[str, Any] | None:
    if not HEALTH_PATH.exists():
        return None

    try:
        return json.loads(HEALTH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None