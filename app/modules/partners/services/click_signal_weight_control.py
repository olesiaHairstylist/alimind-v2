from __future__ import annotations

CLICK_SIGNAL_WEIGHT = 1.0
CLICK_SIGNAL_MAX_EFFECT = 0.15


def _safe_float(value: object) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def clamp_click_signal_effect(value: float) -> float:
    safe_value = _safe_float(value)
    if safe_value is None or safe_value <= 0:
        return 0.0
    return min(safe_value, CLICK_SIGNAL_MAX_EFFECT)


def get_click_signal_weight() -> float:
    safe_weight = _safe_float(CLICK_SIGNAL_WEIGHT)
    if safe_weight is None or safe_weight <= 0:
        return 0.0
    return min(safe_weight, 1.0)


def apply_click_signal_weight(signal: float) -> float:
    safe_signal = _safe_float(signal)
    if safe_signal is None or safe_signal <= 0:
        return 0.0

    from app.modules.partners.services.click_signal_adaptive_control import (
        get_effective_click_signal_weight,
    )

    weighted = safe_signal * get_effective_click_signal_weight()
    return clamp_click_signal_effect(weighted)
