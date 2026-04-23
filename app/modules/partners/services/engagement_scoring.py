from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.partners.services.ab_test import (
    get_engagement_ab_group,
    get_engagement_weight,
)
from app.modules.partners.storage.engagement_memory import get_click_memory


def _get_engagement_score(click_count: int) -> int:
    if click_count <= 0:
        return 0
    if click_count >= 4:
        return 40
    return click_count * 10


def _parse_iso_datetime(value: Any) -> datetime | None:
    normalized_value = str(value or "").strip()
    if not normalized_value:
        return None

    try:
        parsed_value = datetime.fromisoformat(normalized_value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed_value.tzinfo is None:
        return parsed_value.replace(tzinfo=timezone.utc)

    return parsed_value.astimezone(timezone.utc)


def _get_decay_multiplier(last_clicked_at: Any) -> float:
    parsed_last_clicked_at = _parse_iso_datetime(last_clicked_at)
    if parsed_last_clicked_at is None:
        return 1.0

    elapsed = datetime.now(timezone.utc) - parsed_last_clicked_at
    elapsed_days = max(elapsed.days, 0)

    if elapsed_days <= 3:
        return 1.0
    if elapsed_days <= 14:
        return 0.7
    if elapsed_days <= 30:
        return 0.4
    return 0.1


def apply_engagement_scoring(
    offers: list[dict[str, Any]],
    user_key: str,
) -> list[dict[str, Any]]:
    normalized_user_key = str(user_key or "").strip()
    if not normalized_user_key:
        return offers

    try:
        ab_group = get_engagement_ab_group(normalized_user_key)
        engagement_weight = get_engagement_weight(normalized_user_key)
        click_memory = get_click_memory(normalized_user_key)
    except Exception:
        return offers

    scored_offers: list[dict[str, Any]] = []

    for offer in offers:
        offer_id = str(offer.get("id", "")).strip()
        if str(offer.get("status", "")).strip() != "active" or not offer_id:
            scored_offers.append(offer)
            continue

        click_info = click_memory.get(offer_id, {})
        engagement_click_count = int(click_info.get("count", 0))
        engagement_last_clicked_at = str(click_info.get("last_clicked_at", "")).strip()
        engagement_decay_multiplier = _get_decay_multiplier(engagement_last_clicked_at)
        engagement_score = _get_engagement_score(engagement_click_count)
        decayed_engagement_score = round(engagement_score * engagement_decay_multiplier)
        weighted_engagement_score = round(decayed_engagement_score * engagement_weight)
        final_partner_score = int(offer.get("priority", 0)) + weighted_engagement_score

        scored_offers.append(
            {
                **offer,
                "ab_group": ab_group,
                "engagement_click_count": engagement_click_count,
                "engagement_last_clicked_at": engagement_last_clicked_at,
                "engagement_score": engagement_score,
                "engagement_decay_multiplier": engagement_decay_multiplier,
                "decayed_engagement_score": decayed_engagement_score,
                "engagement_weight": engagement_weight,
                "weighted_engagement_score": weighted_engagement_score,
                "final_partner_score": final_partner_score,
            }
        )

    return sorted(
        scored_offers,
        key=lambda offer: (
            -int(offer.get("final_partner_score", int(offer.get("priority", 0)))),
            -int(offer.get("engagement_click_count", 0)),
            str(offer.get("offer_title", "")),
        ),
    )
