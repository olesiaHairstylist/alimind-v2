from __future__ import annotations

import json
from pathlib import Path
from typing import Dict
from datetime import datetime

from app.data.system.source_health_contracts import SourceHealth


# =========================
# PATH
# =========================

BASE_PATH = Path("app/data/system/health")
BASE_PATH.mkdir(parents=True, exist_ok=True)

HEALTH_FILE = BASE_PATH / "city_events_health.json"


# =========================
# LOAD
# =========================

def _load_health_snapshot() -> Dict:
    if not HEALTH_FILE.exists():
        return {
            "type": "health_snapshot",
            "updated_at": None,
            "sources": {}
        }

    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # fallback если файл повреждён
        return {
            "type": "health_snapshot",
            "updated_at": None,
            "sources": {}
        }


# =========================
# SAVE
# =========================

def _save_health_snapshot(data: Dict) -> None:
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# PUBLIC API
# =========================

def write_health(health: SourceHealth) -> None:
    snapshot = _load_health_snapshot()

    # обновляем источник
    snapshot["sources"][health.source_name] = {
        "status": health.status.value,
        "message": health.message,
        "updated_at": health.updated_at,
        "items_count": health.items_count,
        "error_code": health.error_code.value if health.error_code else None,
        "error_details": health.error_details,
        "is_expected_empty": health.is_expected_empty,
        "checked_at": health.checked_at,
    }

    snapshot["updated_at"] = datetime.utcnow().isoformat()

    _save_health_snapshot(snapshot)