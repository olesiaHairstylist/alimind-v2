OPERATOR_DEBUG_VIEW_VERSION = "v1"


def _safe_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def _safe_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _build_operator_snapshot(offer: dict) -> dict:
    explainability = _safe_dict(offer.get("_explainability", {}))
    signals = _safe_dict(explainability.get("signals", {}))
    stages = _safe_dict(explainability.get("stages", {}))
    formula = _safe_dict(explainability.get("formula", {}))

    return {
        "version": OPERATOR_DEBUG_VIEW_VERSION,
        "partner_id": str(offer.get("id", "")),
        "priority": _safe_float(signals.get("priority", 0.0)),
        "engagement_score": _safe_float(signals.get("engagement_score", 0.0)),
        "token_boost": _safe_float(signals.get("token_boost", 0.0)),
        "monetization_boost": _safe_float(signals.get("monetization_boost", 0.0)),
        "impressions": _safe_int(signals.get("debug_impressions", 0)),
        "clicks": _safe_int(signals.get("debug_clicks", 0)),
        "passed_quality_gates": bool(stages.get("passed_quality_gates", False)),
        "token_boost_attached": bool(stages.get("token_boost_attached", False)),
        "monetization_attached": bool(stages.get("monetization_attached", False)),
        "explainable_total": _safe_float(formula.get("explainable_total", 0.0)),
    }


def attach_operator_debug_view(final_offers: list[dict]) -> list[dict]:
    if not final_offers:
        return final_offers

    debug_offers: list[dict] = []

    for offer in final_offers:
        new_offer = dict(offer)
        new_offer["_operator_debug"] = _build_operator_snapshot(offer)
        debug_offers.append(new_offer)

    return debug_offers
