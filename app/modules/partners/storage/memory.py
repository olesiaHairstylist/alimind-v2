from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
MEMORY_PATH = BASE_DIR / "modules" / "partners" / "storage" / "partner_memory.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_memory() -> dict[str, Any]:
    if not MEMORY_PATH.exists():
        return {}

    try:
        payload = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _save_memory(memory: dict[str, Any]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_user_key(user_key: str) -> str:
    value = str(user_key or "").strip()
    return value or "demo"


def get_seen_memory(user_key: str) -> dict[str, dict[str, Any]]:
    normalized_user_key = _normalize_user_key(user_key)
    memory = _load_memory()
    raw_user_block = memory.get(normalized_user_key, {})
    if not isinstance(raw_user_block, dict):
        return {}

    raw_seen = raw_user_block.get("seen", {})
    if not isinstance(raw_seen, dict):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for partner_id, info in raw_seen.items():
        if not isinstance(partner_id, str) or not isinstance(info, dict):
            continue
        result[partner_id] = {
            "count": int(info.get("count", 0)) if str(info.get("count", "0")).isdigit() else 0,
            "last_shown_at": str(info.get("last_shown_at", "")).strip(),
        }

    return result


def mark_offers_shown(user_key: str, partner_ids: list[str]) -> None:
    normalized_user_key = _normalize_user_key(user_key)
    memory = _load_memory()
    user_block = memory.get(normalized_user_key)
    if not isinstance(user_block, dict):
        user_block = {}

    seen = user_block.get("seen")
    if not isinstance(seen, dict):
        seen = {}

    now_iso = _now_iso()
    for partner_id in partner_ids:
        partner_key = str(partner_id).strip()
        if not partner_key:
            continue

        current = seen.get(partner_key)
        if not isinstance(current, dict):
            current = {
                "count": 0,
                "last_shown_at": "",
            }

        current["count"] = int(current.get("count", 0)) + 1
        current["last_shown_at"] = now_iso
        seen[partner_key] = current

    user_block["seen"] = seen
    memory[normalized_user_key] = user_block
    _save_memory(memory)


def clear_seen_memory(user_key: str | None = None) -> None:
    if user_key is None:
        _save_memory({})
        return

    normalized_user_key = _normalize_user_key(user_key)
    memory = _load_memory()
    if normalized_user_key in memory:
        del memory[normalized_user_key]
        _save_memory(memory)
