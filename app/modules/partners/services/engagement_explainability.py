EXPLAINABILITY_VERSION = "v1"


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


def _build_signal_snapshot(offer: dict) -> dict:
    return {
        "priority": _safe_float(offer.get("priority", 0)),
        "engagement_score": _safe_float(offer.get("_engagement_score", 0.0)),
        "token_boost": _safe_float(offer.get("_token_boost", 0.0)),
        "monetization_boost": _safe_float(offer.get("_monetization_boost", 0.0)),
        "debug_impressions": _safe_int(offer.get("_debug_impressions", 0)),
        "debug_clicks": _safe_int(offer.get("_debug_clicks", 0)),
        "debug_token_value": _safe_float(offer.get("_debug_token_value", 0.0)),
        "debug_monetization_value": _safe_float(offer.get("_debug_monetization_value", 0.0)),
    }


def _build_stage_flags(offer: dict) -> dict:
    return {
        "selected": True,
        "scored": True,
        "passed_quality_gates": True,
        "token_boost_attached": "_token_boost" in offer,
        "monetization_attached": "_monetization_boost" in offer,
        "preview_ready": True,
    }


def _build_final_formula_snapshot(offer: dict) -> dict:
    priority_component = _safe_float(offer.get("priority", 0))
    engagement_component = _safe_float(offer.get("_engagement_score", 0.0))
    token_component = _safe_float(offer.get("_token_boost", 0.0))
    monetization_component = _safe_float(offer.get("_monetization_boost", 0.0))

    return {
        "priority_component": priority_component,
        "engagement_component": engagement_component,
        "token_component": token_component,
        "monetization_component": monetization_component,
        "explainable_total": (
            priority_component
            + engagement_component
            + token_component
            + monetization_component
        ),
    }


def attach_explainability(final_offers: list[dict]) -> list[dict]:
    if not final_offers:
        return final_offers

    explained_offers: list[dict] = []

    for offer in final_offers:
        new_offer = dict(offer)
        new_offer["_explainability"] = {
            "version": EXPLAINABILITY_VERSION,
            "signals": _build_signal_snapshot(offer),
            "stages": _build_stage_flags(offer),
            "formula": _build_final_formula_snapshot(offer),
        }
        explained_offers.append(new_offer)

    return explained_offers
