from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
CLICK_EVENTS_PATH = BASE_DIR / "modules" / "partners" / "storage" / "partner_click_events.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_events() -> list[dict[str, Any]]:
    if not CLICK_EVENTS_PATH.exists():
        return []

    try:
        payload = json.loads(CLICK_EVENTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    return payload if isinstance(payload, list) else []


def _save_events(events: list[dict[str, Any]]) -> None:
    CLICK_EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CLICK_EVENTS_PATH.write_text(
        json.dumps(events, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mark_partner_click_event(
    user_key: str,
    session_key: str,
    partner_id: str,
    ab_group: str,
    engagement_weight: float,
    impression_event_id: str,
) -> bool:
    normalized_user_key = str(user_key or "").strip()
    normalized_partner_id = str(partner_id or "").strip()

    if not normalized_user_key or not normalized_partner_id:
        return False

    try:
        events = _load_events()
        events.append(
            {
                "user_key": normalized_user_key,
                "session_key": str(session_key or "").strip(),
                "partner_id": normalized_partner_id,
                "ab_group": str(ab_group or "").strip(),
                "engagement_weight": float(engagement_weight),
                "impression_event_id": str(impression_event_id or "").strip(),
                "clicked_at": _now_iso(),
            }
        )
        _save_events(events)
        return True
    except Exception:
        return False


def read_partner_click_events() -> list[dict[str, Any]]:
    return _load_events()
