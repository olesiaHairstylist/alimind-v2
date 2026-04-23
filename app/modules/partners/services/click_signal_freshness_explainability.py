from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.partners.services.click_signals import get_last_clicked_at

FRESH_SECONDS = 24 * 60 * 60
AGING_SECONDS = 7 * 24 * 60 * 60


def _parse_iso_datetime(value: str | None) -> datetime | None:
    raw_value = str(value or "").strip()
    if not raw_value:
        return None

    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _get_signal_age_seconds(last_clicked_at: str | None) -> int | None:
    parsed = _parse_iso_datetime(last_clicked_at)
    if parsed is None:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    age_seconds = int((now - parsed).total_seconds())
    return max(0, age_seconds)


def _get_freshness_state(signal_age_seconds: int | None) -> str:
    if signal_age_seconds is None:
        return "unknown"
    if signal_age_seconds <= FRESH_SECONDS:
        return "fresh"
    if signal_age_seconds <= AGING_SECONDS:
        return "aging"
    return "stale"


def explain_click_signal_freshness(partner_id: str) -> dict[str, Any]:
    normalized_partner_id = str(partner_id or "").strip()
    last_clicked_at = get_last_clicked_at(normalized_partner_id)
    signal_age_seconds = _get_signal_age_seconds(last_clicked_at)

    return {
        "partner_id": normalized_partner_id,
        "last_clicked_at": last_clicked_at,
        "signal_age_seconds": signal_age_seconds,
        "freshness_state": _get_freshness_state(signal_age_seconds),
    }
