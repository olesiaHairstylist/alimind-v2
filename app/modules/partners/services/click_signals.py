from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]
CLICK_SIGNALS_PATH = BASE_DIR / "data" / "system" / "click_signals.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_storage() -> dict[str, Any]:
    return {
        "type": "click_signals_v1",
        "updated_at": _now_iso(),
        "partners": {},
    }


def _normalize_storage(data: Any) -> dict[str, Any]:
    payload = data if isinstance(data, dict) else {}
    raw_partners = payload.get("partners", {})
    partners: dict[str, dict[str, Any]] = {}

    if isinstance(raw_partners, dict):
        for partner_id, value in raw_partners.items():
            normalized_partner_id = str(partner_id or "").strip()
            if not normalized_partner_id or not isinstance(value, dict):
                continue

            try:
                clicks = int(value.get("clicks", 0))
            except Exception:
                clicks = 0

            partners[normalized_partner_id] = {
                "clicks": max(0, clicks),
                "last_clicked_at": str(value.get("last_clicked_at", "")).strip(),
            }

    return {
        "type": "click_signals_v1",
        "updated_at": str(payload.get("updated_at", "")).strip() or _now_iso(),
        "partners": partners,
    }


def load_storage() -> dict[str, Any]:
    if not CLICK_SIGNALS_PATH.exists():
        data = _default_storage()
        save_storage(data)
        return data

    try:
        payload = json.loads(CLICK_SIGNALS_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = _default_storage()
        save_storage(data)
        return data

    data = _normalize_storage(payload)
    if data != payload:
        save_storage(data)
    return data


def save_storage(data: dict) -> None:
    normalized = _normalize_storage(data)
    normalized["updated_at"] = _now_iso()

    CLICK_SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = CLICK_SIGNALS_PATH.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_path.replace(CLICK_SIGNALS_PATH)


def increment_click(partner_id: str) -> None:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return

    data = load_storage()
    partners = data.setdefault("partners", {})
    current = partners.get(normalized_partner_id)

    if not isinstance(current, dict):
        current = {"clicks": 0}

    try:
        clicks = int(current.get("clicks", 0))
    except Exception:
        clicks = 0

    last_clicked_at = _now_iso()
    partners[normalized_partner_id] = {
        "clicks": max(0, clicks) + 1,
        "last_clicked_at": last_clicked_at,
    }
    save_storage(data)


def get_clicks(partner_id: str) -> int:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return 0

    data = load_storage()
    partners = data.get("partners", {})
    if not isinstance(partners, dict):
        return 0

    current = partners.get(normalized_partner_id)
    if not isinstance(current, dict):
        return 0

    try:
        return max(0, int(current.get("clicks", 0)))
    except Exception:
        return 0


def get_last_clicked_at(partner_id: str) -> str | None:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return None

    data = load_storage()
    partners = data.get("partners", {})
    if not isinstance(partners, dict):
        return None

    current = partners.get(normalized_partner_id)
    if not isinstance(current, dict):
        return None

    last_clicked_at = str(current.get("last_clicked_at", "")).strip()
    return last_clicked_at or None
