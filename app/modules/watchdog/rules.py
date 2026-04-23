from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.modules.watchdog.contracts import CITY_EVENT_FILES, EXPECTED_EMPTY, PUBLIC_CITY_EVENTS_DIR


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return raw if isinstance(raw, dict) else None


def _parse_updated_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        pass

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue

    return None


def evaluate(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    try:
        now = datetime.now(timezone.utc)

        for key, filename in CITY_EVENT_FILES.items():
            path = PUBLIC_CITY_EVENTS_DIR / filename

            if not path.exists():
                issues.append({"id": f"{key}_missing_file", "level": "critical"})
                continue

            payload = _load_json(path)
            if payload is None:
                issues.append({"id": f"{key}_invalid_json", "level": "critical"})
                continue

            status = str(payload.get("status", "")).strip().lower()
            if status == "error":
                issues.append({"id": f"{key}_error", "level": "critical"})

            updated_at = _parse_updated_at(payload.get("updated_at"))
            if updated_at is None:
                issues.append({"id": f"{key}_updated_at_invalid", "level": "warning"})
            else:
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                if now - updated_at.astimezone(timezone.utc) > timedelta(hours=24):
                    issues.append({"id": f"{key}_stale", "level": "warning"})

            if status == "empty" and not EXPECTED_EMPTY.get(key, False):
                issues.append({"id": f"{key}_empty_unexpected", "level": "warning"})
    except Exception:
        issues.append({"id": "watchdog_rules_failed", "level": "critical"})

    return issues

