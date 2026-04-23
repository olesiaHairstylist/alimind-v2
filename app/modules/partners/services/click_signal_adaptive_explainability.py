from __future__ import annotations

from typing import Any

from app.modules.partners.services.click_signal_adaptive_control import (
    explain_adaptive_click_signal_weight as _explain_adaptive_state,
)

SAFE_FALLBACK_REASON = "safe_fallback"


def _safe_float(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _normalize_reason(value: object) -> str:
    reason = str(value or "").strip().lower()
    if reason == "base_weight_disabled":
        return "disabled_by_base_weight"
    if reason in {"default", "low_signal_readiness", "disabled_by_base_weight"}:
        return reason
    return SAFE_FALLBACK_REASON


def explain_adaptive_click_signal_weight() -> dict[str, Any]:
    try:
        payload = _explain_adaptive_state()
    except Exception:
        payload = {}

    base_weight = _safe_float(payload.get("base_weight", 0.0))
    adaptive_multiplier = _safe_float(payload.get("adaptive_multiplier", 1.0))
    effective_weight = _safe_float(payload.get("effective_weight", 0.0))
    reason = _normalize_reason(payload.get("reason", SAFE_FALLBACK_REASON))

    return {
        "base_weight": base_weight,
        "adaptive_multiplier": adaptive_multiplier,
        "effective_weight": effective_weight,
        "is_dampened": effective_weight < base_weight,
        "is_disabled": effective_weight <= 0.0,
        "has_base_weight": base_weight > 0.0,
        "reason": reason,
    }
