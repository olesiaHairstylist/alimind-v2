MIN_QUALITY_IMPRESSIONS = 10


def _is_valid_priority(value: object) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def apply_quality_gates(offers: list[dict]) -> list[dict]:
    if not offers:
        return offers

    filtered_offers: list[dict] = []

    for offer in offers:
        partner_id = str(offer.get("id", "")).strip()
        priority = offer.get("priority", 0)
        impressions = int(offer.get("_debug_impressions", 0) or 0)
        clicks = int(offer.get("_debug_clicks", 0) or 0)

        if not partner_id:
            continue

        if not _is_valid_priority(priority):
            continue

        if impressions >= MIN_QUALITY_IMPRESSIONS and clicks <= 0:
            continue

        filtered_offers.append(dict(offer))

    return filtered_offers
