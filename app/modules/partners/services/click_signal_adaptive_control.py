from __future__ import annotations

import json
from typing import Any

from app.modules.partners.services.click_signals import (
    CLICK_SIGNALS_PATH,
    _normalize_storage,
)
from app.modules.partners.services.click_signal_weight_control import (
    get_click_signal_weight,
)

DEFAULT_ADAPTIVE_MULTIPLIER = 1.0
LOW_SIGNAL_MULTIPLIER = 0.85


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


def get_base_click_signal_weight() -> float:
    return get_click_signal_weight()


def get_adaptive_click_signal_multiplier() -> float:
    storage = _load_storage_read_only()
    partners = storage.get("partners", {})
    if not isinstance(partners, dict):
        return DEFAULT_ADAPTIVE_MULTIPLIER

    positive_partner_count = 0
    total_clicks = 0

    for payload in partners.values():
        if not isinstance(payload, dict):
            continue
        try:
            clicks = max(0, int(payload.get("clicks", 0)))
        except Exception:
            clicks = 0

        if clicks <= 0:
            continue

        positive_partner_count += 1
        total_clicks += clicks

    if positive_partner_count == 1 and total_clicks == 1:
        return LOW_SIGNAL_MULTIPLIER

    return DEFAULT_ADAPTIVE_MULTIPLIER


def get_effective_click_signal_weight() -> float:
    base_weight = get_base_click_signal_weight()
    if base_weight <= 0:
        return 0.0

    multiplier = get_adaptive_click_signal_multiplier()
    try:
        effective_weight = float(base_weight) * float(multiplier)
    except Exception:
        return float(base_weight)

    if effective_weight <= 0:
        return 0.0

    return min(float(base_weight), effective_weight)


def explain_adaptive_click_signal_weight() -> dict[str, Any]:
    base_weight = get_base_click_signal_weight()
    adaptive_multiplier = get_adaptive_click_signal_multiplier()
    effective_weight = get_effective_click_signal_weight()

    reason = "default"
    if base_weight <= 0:
        reason = "base_weight_disabled"
    elif adaptive_multiplier < DEFAULT_ADAPTIVE_MULTIPLIER:
        reason = "low_signal_readiness"

    return {
        "base_weight": base_weight,
        "adaptive_multiplier": adaptive_multiplier,
        "effective_weight": effective_weight,
        "reason": reason,
    }
