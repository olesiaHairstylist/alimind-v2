from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from app.modules.watchdog.contracts import ALERT_COOLDOWN_SECONDS, STATE_PATH


def _load_state() -> dict[str, Any]:
    try:
        if not STATE_PATH.exists():
            return {}
        raw = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _save_state(data: dict[str, Any]) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        return


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def should_alert(issue_id: str) -> bool:
    try:
        state = _load_state()
        last_sent_raw = state.get(issue_id)
        last_sent = _parse_iso(last_sent_raw)
        if last_sent is None:
            return True
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=timezone.utc)
        cooldown = timedelta(seconds=ALERT_COOLDOWN_SECONDS)
        return datetime.now(timezone.utc) - last_sent.astimezone(timezone.utc) >= cooldown
    except Exception:
        return True


def save_alert(issue_id: str) -> None:
    try:
        state = _load_state()
        state[issue_id] = datetime.now(timezone.utc).isoformat()
        _save_state(state)
    except Exception:
        return

