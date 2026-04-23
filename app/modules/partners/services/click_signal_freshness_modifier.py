from __future__ import annotations

from app.modules.partners.services.click_signal_freshness_explainability import (
    explain_click_signal_freshness,
)


def apply_freshness_modifier(partner_id: str, signal: float) -> float:
    if not signal:
        return 0.0

    try:
        freshness = explain_click_signal_freshness(partner_id)
        state = freshness.get("freshness_state", "unknown")
    except Exception:
        return 0.0

    if state == "fresh":
        return signal
    if state == "aging":
        return signal * 0.7
    if state == "stale":
        return signal * 0.3
    return 0.0
