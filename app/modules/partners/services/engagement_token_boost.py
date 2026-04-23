DEFAULT_TOKEN_BOOST_ENABLED = True
MAX_TOKEN_BOOST = 0.15


def is_token_boost_enabled() -> bool:
    return DEFAULT_TOKEN_BOOST_ENABLED


def _safe_token_value(value: object) -> float:
    try:
        token_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if token_value < 0:
        return 0.0

    return float(token_value)


def _normalize_token_boost(token_value: float) -> float:
    if token_value <= 0:
        return 0.0

    return min(token_value / 100.0, MAX_TOKEN_BOOST)


def apply_token_boost(offers: list[dict]) -> list[dict]:
    if not offers:
        return offers

    if is_token_boost_enabled() is False:
        return offers

    boosted_offers: list[dict] = []

    for offer in offers:
        token_value = _safe_token_value(offer.get("_debug_token_value", 0.0))
        token_boost = _normalize_token_boost(token_value)

        new_offer = dict(offer)
        new_offer["_token_boost"] = token_boost
        boosted_offers.append(new_offer)

    return boosted_offers
