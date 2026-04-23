from __future__ import annotations

from app.modules.partners.services.click_signal_freshness_explainability import (
    explain_click_signal_freshness,
)


def apply_freshness_weight_balance(partner_id: str, weighted_signal: float) -> float:
    if not weighted_signal:
        return 0.0

    try:
        freshness = explain_click_signal_freshness(partner_id)
        state = freshness.get("freshness_state", "unknown")
    except Exception:
        return 0.0

    if state == "fresh":
        return weighted_signal
    if state == "aging":
        return weighted_signal * 0.85
    if state == "stale":
        return weighted_signal * 0.5
    return 0.0
