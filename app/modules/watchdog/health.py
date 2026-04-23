from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.modules.watchdog.contracts import ALLOWED_STATUSES, CITY_EVENT_FILES, PUBLIC_CITY_EVENTS_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    return raw if isinstance(raw, dict) else None


def _resolve_status(path: Path) -> str:
    try:
        if not path.exists():
            return "error"

        payload = _load_json(path)
        if payload is None:
            return "error"

        status = payload.get("status")
        updated_at = payload.get("updated_at")

        if not isinstance(status, str) or status not in ALLOWED_STATUSES:
            return "error"

        if not isinstance(updated_at, str) or not updated_at.strip():
            return "error"

        return status
    except Exception:
        return "error"


def run_health_check() -> dict[str, str]:
    result: dict[str, str] = {}

    try:
        for key, filename in CITY_EVENT_FILES.items():
            result[key] = _resolve_status(PUBLIC_CITY_EVENTS_DIR / filename)
    except Exception:
        for key in CITY_EVENT_FILES:
            result.setdefault(key, "error")

    result["timestamp"] = _now_iso()
    return result

