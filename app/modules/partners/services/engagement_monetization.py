DEFAULT_MONETIZATION_ENABLED = True
MAX_MONETIZATION_BOOST = 0.10


def is_monetization_enabled() -> bool:
    return DEFAULT_MONETIZATION_ENABLED


def _safe_monetization_value(value: object) -> float:
    try:
        monetization_value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if monetization_value < 0:
        return 0.0

    return float(monetization_value)


def _normalize_monetization_boost(value: float) -> float:
    if value <= 0:
        return 0.0

    return min(value / 100.0, MAX_MONETIZATION_BOOST)


def apply_monetization_signal(offers: list[dict]) -> list[dict]:
    if not offers:
        return offers

    if is_monetization_enabled() is False:
        return offers

    monetized_offers: list[dict] = []

    for offer in offers:
        raw_value = offer.get("_debug_monetization_value", 0.0)
        normalized_value = _normalize_monetization_boost(
            _safe_monetization_value(raw_value)
        )

        new_offer = dict(offer)
        new_offer["_monetization_boost"] = normalized_value
        monetized_offers.append(new_offer)

    return monetized_offers
