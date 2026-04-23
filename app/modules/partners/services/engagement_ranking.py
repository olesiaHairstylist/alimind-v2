from typing import List, Dict


# --- CONFIG (V3 BASELINE, SAFE MODE) ---
MIN_IMPRESSIONS = 20

W_CTR = 0.5
W_BOOST = 0.3
W_FRESH = 0.1
W_BASE = 0.1


# --- HELPERS ---

def _safe_ctr(clicks: int, impressions: int) -> float:
    if impressions <= 0:
        return 0.0
    return clicks / impressions


def _normalize(value: float, max_value: float = 1.0) -> float:
    if max_value <= 0:
        return 0.0
    return min(value / max_value, 1.0)


def _boost(tokens_spent: float) -> float:
    # log smoothing
    import math
    return math.log(1 + max(tokens_spent, 0.0))


# --- MAIN CALCULATION ---

def compute_partner_score(
    partner_id: str,
    stats: Dict[str, Dict],
    tokens: Dict[str, float],
) -> float:

    partner_stats = stats.get(partner_id, {})
    impressions = partner_stats.get("impressions", 0)
    clicks = partner_stats.get("clicks", 0)

    # --- CTR ---
    ctr = _safe_ctr(clicks, impressions)

    if impressions < MIN_IMPRESSIONS:
        ctr_score = 0.5  # neutral baseline
    else:
        ctr_score = _normalize(ctr)

    # --- BOOST ---
    token_value = tokens.get(partner_id, 0.0)
    boost_score = _boost(token_value)

    # --- FRESHNESS (stub) ---
    freshness_score = 0.5

    # --- BASE ---
    base_score = 0.5

    final_score = (
        W_CTR * ctr_score +
        W_BOOST * boost_score +
        W_FRESH * freshness_score +
        W_BASE * base_score
    )

    return round(final_score, 4)


# --- BULK (NO SIDE EFFECTS) ---

def compute_scores_for_offers(
    offers: List[Dict],
    stats: Dict[str, Dict],
    tokens: Dict[str, float],
) -> List[Dict]:
    enriched = []

    for offer in offers:
        pid = str(offer.get("id", ""))
        partner_stats = stats.get(pid, {})

        impressions = partner_stats.get("impressions", 0)
        clicks = partner_stats.get("clicks", 0)

        ctr = _safe_ctr(clicks, impressions)

        if impressions < MIN_IMPRESSIONS:
            ctr_score = 0.5
        else:
            ctr_score = _normalize(ctr)

        token_value = tokens.get(pid, 0.0)
        boost_score = _boost(token_value)

        freshness_score = 0.5
        base_score = 0.5

        final_score = (
            W_CTR * ctr_score +
            W_BOOST * boost_score +
            W_FRESH * freshness_score +
            W_BASE * base_score
        )

        new_offer = dict(offer)

        new_offer["_engagement_score"] = round(final_score, 4)

        # --- DEBUG BLOCK ---
        new_offer["_debug_impressions"] = impressions
        new_offer["_debug_clicks"] = clicks
        new_offer["_debug_ctr"] = round(ctr, 4)
        new_offer["_debug_ctr_score"] = round(ctr_score, 4)
        new_offer["_debug_boost_score"] = round(boost_score, 4)
        new_offer["_debug_freshness_score"] = freshness_score
        new_offer["_debug_base_score"] = base_score

        enriched.append(new_offer)

    return enriched
