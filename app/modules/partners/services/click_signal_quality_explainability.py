from __future__ import annotations

from typing import Any

from app.modules.partners.services.click_signal_quality_gate import (
    MIN_USABLE_CLICKS,
    get_click_signal_quality_state,
    get_quality_gated_click_signal,
)

SAFE_FALLBACK_REASON = "safe_fallback"


def _safe_float(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _normalize_reason(value: object) -> str:
    reason = str(value or "").strip().lower()
    if reason in {
        "missing_partner",
        "no_guarded_signal",
        "low_signal_quality",
        "usable",
        "safe_fallback",
    }:
        return reason
    return SAFE_FALLBACK_REASON


def explain_click_signal_quality(partner_id: str) -> dict[str, Any]:
    normalized_partner_id = str(partner_id or "").strip()

    try:
        state = get_click_signal_quality_state(normalized_partner_id)
        gated_signal = get_quality_gated_click_signal(normalized_partner_id)
    except Exception:
        return {
            "partner_id": normalized_partner_id,
            "raw_clicks": 0,
            "guarded_signal": 0.0,
            "usable": False,
            "reason": SAFE_FALLBACK_REASON,
            "gated_signal": 0.0,
            "min_usable_clicks": MIN_USABLE_CLICKS,
        }

    return {
        "partner_id": str(state.get("partner_id", "")).strip(),
        "raw_clicks": max(0, _safe_int(state.get("raw_clicks", 0))),
        "guarded_signal": max(0.0, _safe_float(state.get("guarded_signal", 0.0))),
        "usable": bool(state.get("usable", False)),
        "reason": _normalize_reason(state.get("reason", SAFE_FALLBACK_REASON)),
        "gated_signal": max(0.0, _safe_float(gated_signal)),
        "min_usable_clicks": MIN_USABLE_CLICKS,
    }
