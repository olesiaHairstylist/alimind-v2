from __future__ import annotations

from typing import Any

from app.modules.partners.services.click_signal_guard import get_guarded_click_signal
from app.modules.partners.services.click_signal_weight_control import (
    CLICK_SIGNAL_MAX_EFFECT,
    apply_click_signal_weight,
    get_click_signal_weight,
)


def explain_click_signal(partner_id: str) -> dict[str, Any]:
    normalized_partner_id = str(partner_id or "").strip()
    if not normalized_partner_id:
        return {
            "partner_id": "",
            "guarded_signal": 0.0,
            "weighted_signal": 0.0,
            "has_signal": False,
            "is_zero_effect": True,
            "is_capped": False,
            "weight": get_click_signal_weight(),
            "max_effect": CLICK_SIGNAL_MAX_EFFECT,
        }

    guarded_signal = get_guarded_click_signal(normalized_partner_id)
    weighted_signal = apply_click_signal_weight(guarded_signal)

    return {
        "partner_id": normalized_partner_id,
        "guarded_signal": guarded_signal,
        "weighted_signal": weighted_signal,
        "has_signal": guarded_signal > 0.0,
        "is_zero_effect": weighted_signal <= 0.0,
        "is_capped": weighted_signal >= CLICK_SIGNAL_MAX_EFFECT,
        "weight": get_click_signal_weight(),
        "max_effect": CLICK_SIGNAL_MAX_EFFECT,
    }
