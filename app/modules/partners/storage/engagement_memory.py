from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
ENGAGEMENT_MEMORY_PATH = BASE_DIR / "modules" / "partners" / "storage" / "partner_engagement_memory.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_memory() -> dict[str, Any]:
    if not ENGAGEMENT_MEMORY_PATH.exists():
        return {}

    try:
        payload = json.loads(ENGAGEMENT_MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _save_memory(memory: dict[str, Any]) -> None:
    ENGAGEMENT_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENGAGEMENT_MEMORY_PATH.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_user_key(user_key: str) -> str:
    value = str(user_key or "").strip()
    return value or "unknown"


def mark_partner_click(user_key: str, partner_id: str) -> bool:
    normalized_user_key = _normalize_user_key(user_key)
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return False

    try:
        memory = _load_memory()
        user_block = memory.get(normalized_user_key)
        if not isinstance(user_block, dict):
            user_block = {}

        clicks = user_block.get("clicks")
        if not isinstance(clicks, dict):
            clicks = {}

        current = clicks.get(normalized_partner_id)
        if not isinstance(current, dict):
            current = {
                "count": 0,
                "last_clicked_at": "",
            }

        current["count"] = int(current.get("count", 0)) + 1
        current["last_clicked_at"] = _now_iso()
        clicks[normalized_partner_id] = current

        user_block["clicks"] = clicks
        memory[normalized_user_key] = user_block
        _save_memory(memory)
        return True
    except Exception:
        return False


def get_click_memory(user_key: str) -> dict[str, dict[str, Any]]:
    normalized_user_key = _normalize_user_key(user_key)
    memory = _load_memory()
    user_block = memory.get(normalized_user_key, {})
    if not isinstance(user_block, dict):
        return {}

    clicks = user_block.get("clicks", {})
    if not isinstance(clicks, dict):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for partner_id, payload in clicks.items():
        if not isinstance(partner_id, str) or not isinstance(payload, dict):
            continue
        result[partner_id] = {
            "count": int(payload.get("count", 0)) if str(payload.get("count", "0")).isdigit() else 0,
            "last_clicked_at": str(payload.get("last_clicked_at", "")).strip(),
        }

    return result


def clear_click_memory(user_key: str | None = None) -> None:
    if user_key is None:
        _save_memory({})
        return

    normalized_user_key = _normalize_user_key(user_key)
    memory = _load_memory()
    if normalized_user_key in memory:
        del memory[normalized_user_key]
        _save_memory(memory)

