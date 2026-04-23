from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
SESSION_MEMORY_PATH = BASE_DIR / "modules" / "partners" / "storage" / "partner_session_memory.json"


def _load_memory() -> dict[str, Any]:
    if not SESSION_MEMORY_PATH.exists():
        return {}

    try:
        payload = json.loads(SESSION_MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _save_memory(memory: dict[str, Any]) -> None:
    SESSION_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_MEMORY_PATH.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_session_key(session_key: str) -> str:
    value = str(session_key or "").strip()
    return value or "demo_session"


def get_session_state(session_key: str) -> dict[str, Any]:
    normalized_session_key = _normalize_session_key(session_key)
    memory = _load_memory()
    raw_session_block = memory.get(normalized_session_key, {})
    if not isinstance(raw_session_block, dict):
        return {
            "shown": [],
            "counts": {},
            "last_displayed": [],
        }

    shown = raw_session_block.get("shown", [])
    counts = raw_session_block.get("counts", {})
    last_displayed = raw_session_block.get("last_displayed", [])

    return {
        "shown": [str(item).strip() for item in shown if str(item).strip()] if isinstance(shown, list) else [],
        "counts": {
            str(key).strip(): int(value)
            for key, value in counts.items()
            if str(key).strip() and str(value).isdigit()
        } if isinstance(counts, dict) else {},
        "last_displayed": [str(item).strip() for item in last_displayed if str(item).strip()] if isinstance(last_displayed, list) else [],
    }


def get_session_shown(session_key: str) -> list[str]:
    return list(get_session_state(session_key)["shown"])


def mark_session_shown(session_key: str, partner_ids: list[str]) -> None:
    normalized_session_key = _normalize_session_key(session_key)
    memory = _load_memory()
    session_block = memory.get(normalized_session_key)
    if not isinstance(session_block, dict):
        session_block = {}

    shown = session_block.get("shown", [])
    if not isinstance(shown, list):
        shown = []

    counts = session_block.get("counts", {})
    if not isinstance(counts, dict):
        counts = {}

    normalized_partner_ids: list[str] = []
    for partner_id in partner_ids:
        partner_key = str(partner_id).strip()
        if not partner_key:
            continue

        normalized_partner_ids.append(partner_key)
        if partner_key not in shown:
            shown.append(partner_key)

        counts[partner_key] = int(counts.get(partner_key, 0)) + 1

    session_block["shown"] = shown
    session_block["counts"] = counts
    session_block["last_displayed"] = normalized_partner_ids
    memory[normalized_session_key] = session_block
    _save_memory(memory)


def clear_session_memory(session_key: str | None = None) -> None:
    if session_key is None:
        _save_memory({})
        return

    normalized_session_key = _normalize_session_key(session_key)
    memory = _load_memory()
    if normalized_session_key in memory:
        del memory[normalized_session_key]
        _save_memory(memory)
