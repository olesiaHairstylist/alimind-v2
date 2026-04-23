from __future__ import annotations

import json
from typing import Any

from app.modules.partners.services.click_signals import (
    CLICK_SIGNALS_PATH,
    _normalize_storage,
)

MAX_GUARDED_SIGNAL = 0.15
_GUARD_STEPS: tuple[tuple[int, float], ...] = (
    (1, 0.02),
    (2, 0.03),
    (3, 0.04),
    (5, 0.06),
    (10, 0.08),
    (20, 0.10),
    (50, MAX_GUARDED_SIGNAL),
)


def _default_storage() -> dict[str, Any]:
    return {
        "type": "click_signals_v1",
        "updated_at": "",
        "partners": {},
    }


def _load_storage_read_only() -> dict[str, Any]:
    if not CLICK_SIGNALS_PATH.exists():
        return _default_storage()

    try:
        payload = json.loads(CLICK_SIGNALS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _default_storage()

    try:
        return _normalize_storage(payload)
    except Exception:
        return _default_storage()


def get_raw_clicks(partner_id: str) -> int:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return 0

    storage = _load_storage_read_only()
    partners = storage.get("partners", {})
    if not isinstance(partners, dict):
        return 0

    payload = partners.get(normalized_partner_id)
    if not isinstance(payload, dict):
        return 0

    try:
        return max(0, int(payload.get("clicks", 0)))
    except Exception:
        return 0


def normalize_clicks_to_guarded_signal(clicks: int) -> float:
    try:
        normalized_clicks = int(clicks)
    except Exception:
        return 0.0

    if normalized_clicks <= 0:
        return 0.0

    for threshold, signal in _GUARD_STEPS:
        if normalized_clicks <= threshold:
            return signal

    return MAX_GUARDED_SIGNAL


def get_guarded_click_signal(partner_id: str) -> float:
    return normalize_clicks_to_guarded_signal(get_raw_clicks(partner_id))
