from __future__ import annotations

from typing import Any

from app.modules.partners.services.click_signal_guard import (
    get_guarded_click_signal,
    get_raw_clicks,
)

MIN_USABLE_CLICKS = 2


def get_click_signal_quality_state(partner_id: str) -> dict[str, Any]:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return {
            "partner_id": "",
            "usable": False,
            "reason": "missing_partner",
            "raw_clicks": 0,
            "guarded_signal": 0.0,
        }

    try:
        raw_clicks = get_raw_clicks(normalized_partner_id)
        guarded_signal = get_guarded_click_signal(normalized_partner_id)
    except Exception:
        return {
            "partner_id": normalized_partner_id,
            "usable": False,
            "reason": "safe_fallback",
            "raw_clicks": 0,
            "guarded_signal": 0.0,
        }

    if guarded_signal <= 0.0:
        return {
            "partner_id": normalized_partner_id,
            "usable": False,
            "reason": "no_guarded_signal",
            "raw_clicks": max(0, int(raw_clicks)),
            "guarded_signal": 0.0,
        }

    if raw_clicks < MIN_USABLE_CLICKS:
        return {
            "partner_id": normalized_partner_id,
            "usable": False,
            "reason": "low_signal_quality",
            "raw_clicks": max(0, int(raw_clicks)),
            "guarded_signal": float(guarded_signal),
        }

    return {
        "partner_id": normalized_partner_id,
        "usable": True,
        "reason": "usable",
        "raw_clicks": max(0, int(raw_clicks)),
        "guarded_signal": float(guarded_signal),
    }


def is_click_signal_usable(partner_id: str) -> bool:
    return bool(get_click_signal_quality_state(partner_id).get("usable", False))


def get_quality_gated_click_signal(partner_id: str) -> float:
    state = get_click_signal_quality_state(partner_id)
    if not bool(state.get("usable", False)):
        return 0.0

    try:
        return max(0.0, float(state.get("guarded_signal", 0.0)))
    except Exception:
        return 0.0
