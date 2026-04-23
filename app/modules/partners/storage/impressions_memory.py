from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[3]
IMPRESSIONS_MEMORY_PATH = BASE_DIR / "modules" / "partners" / "storage" / "partner_impressions_memory.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_event_id() -> str:
    return f"imp_{uuid4().hex}"


def _load_events() -> list[dict[str, Any]]:
    if not IMPRESSIONS_MEMORY_PATH.exists():
        return []

    try:
        payload = json.loads(IMPRESSIONS_MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    return payload if isinstance(payload, list) else []


def _save_events(events: list[dict[str, Any]]) -> None:
    IMPRESSIONS_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    IMPRESSIONS_MEMORY_PATH.write_text(
        json.dumps(events, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mark_partner_impression(
    user_key: str,
    session_key: str,
    ab_group: str,
    engagement_weight: float,
    partner_ids: list[str],
) -> str:
    normalized_user_key = str(user_key or "").strip()
    normalized_session_key = str(session_key or "").strip()
    normalized_partner_ids = [
        str(partner_id).strip()
        for partner_id in partner_ids
        if str(partner_id).strip()
    ]

    if not normalized_user_key or not normalized_session_key or not normalized_partner_ids:
        return ""

    try:
        events = _load_events()
        event_id = _new_event_id()
        events.append(
            {
                "event_id": event_id,
                "user_key": normalized_user_key,
                "session_key": normalized_session_key,
                "ab_group": str(ab_group or "").strip(),
                "engagement_weight": float(engagement_weight),
                "partner_ids": normalized_partner_ids,
                "shown_at": _now_iso(),
            }
        )
        _save_events(events)
        return event_id
    except Exception:
        return ""


def find_latest_matching_impression_event_id(
    user_key: str,
    partner_id: str,
    session_key: str = "",
) -> str:
    normalized_user_key = str(user_key or "").strip()
    normalized_partner_id = str(partner_id or "").strip()
    normalized_session_key = str(session_key or "").strip()

    if not normalized_user_key or not normalized_partner_id:
        return ""

    try:
        events = _load_events()
    except Exception:
        return ""

    latest_fallback_event_id = ""

    for event in reversed(events):
        if not isinstance(event, dict):
            continue

        event_user_key = str(event.get("user_key", "")).strip()
        event_id = str(event.get("event_id", "")).strip()
        partner_ids = event.get("partner_ids", [])

        if (
            event_user_key != normalized_user_key
            or not event_id
            or not isinstance(partner_ids, list)
            or normalized_partner_id not in {str(item).strip() for item in partner_ids if str(item).strip()}
        ):
            continue

        event_session_key = str(event.get("session_key", "")).strip()
        if normalized_session_key and event_session_key == normalized_session_key:
            return event_id

        if not latest_fallback_event_id:
            latest_fallback_event_id = event_id

    return latest_fallback_event_id


def read_partner_impressions() -> list[dict[str, Any]]:
    return _load_events()
