AUDIT_TRACE_VERSION = "v1"


def _safe_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def _safe_bool(value: object) -> bool:
    return bool(value)


def _build_stage_trace(offer: dict) -> list[dict]:
    explainability = _safe_dict(offer.get("_explainability", {}))
    stages = _safe_dict(explainability.get("stages", {}))

    return [
        {"stage": "selection", "applied": True},
        {"stage": "scoring", "applied": True},
        {"stage": "quality_gates", "applied": _safe_bool(stages.get("passed_quality_gates", False))},
        {"stage": "token_boost", "applied": _safe_bool(stages.get("token_boost_attached", False))},
        {"stage": "monetization", "applied": _safe_bool(stages.get("monetization_attached", False))},
        {"stage": "preview_reorder", "applied": True},
        {"stage": "explainability", "applied": _safe_bool("_explainability" in offer)},
        {"stage": "operator_debug_view", "applied": _safe_bool("_operator_debug" in offer)},
        {"stage": "audit_trace", "applied": True},
        {"stage": "render_ready", "applied": True},
    ]


def _build_audit_summary(offer: dict) -> dict:
    operator_debug = _safe_dict(offer.get("_operator_debug", {}))

    return {
        "partner_id": str(offer.get("id", "")),
        "passed_quality_gates": _safe_bool(operator_debug.get("passed_quality_gates", False)),
        "token_boost_attached": _safe_bool(operator_debug.get("token_boost_attached", False)),
        "monetization_attached": _safe_bool(operator_debug.get("monetization_attached", False)),
        "final_debug_available": _safe_bool("_operator_debug" in offer),
        "final_explainability_available": _safe_bool("_explainability" in offer),
    }


def attach_audit_trace(final_offers: list[dict]) -> list[dict]:
    if not final_offers:
        return final_offers

    traced_offers: list[dict] = []

    for offer in final_offers:
        new_offer = dict(offer)
        new_offer["_audit_trace"] = {
            "version": AUDIT_TRACE_VERSION,
            "summary": _build_audit_summary(offer),
            "trace": _build_stage_trace(offer),
        }
        traced_offers.append(new_offer)

    return traced_offers
