from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[3]
HEALTH_PATH = BASE_DIR / "data" / "system" / "health" / "city_events_health.json"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_health(status_map: dict[str, Any]) -> None:
    HEALTH_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "type": "health_snapshot",
        "updated_at": _now_iso(),
        "sources": status_map,
    }

    HEALTH_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )