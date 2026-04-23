from __future__ import annotations

from typing import Any

from app.modules.partners.storage.click_events_memory import read_partner_click_events
from app.modules.partners.storage.impressions_memory import read_partner_impressions

V2_LIMITATIONS_NOTE = (
    "V2 limitation: linking uses the latest matching impression by user_key + partner_id "
    "(+ session_key if available), but callbacks still do not carry explicit impression_event_id."
)


def _safe_ctr(clicks: int, impressions: int) -> float:
    if impressions <= 0:
        return 0.0
    return round(clicks / impressions, 4)


def _read_all_click_events() -> list[dict[str, Any]]:
    try:
        events = read_partner_click_events()
    except Exception:
        return []

    return events if isinstance(events, list) else []


def _aggregate_partner_clicks(
    events: list[dict[str, Any]],
) -> dict[str, int]:
    partner_clicks: dict[str, int] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        normalized_partner_id = str(event.get("partner_id", "")).strip()
        if not normalized_partner_id:
            continue

        partner_clicks[normalized_partner_id] = (
            partner_clicks.get(normalized_partner_id, 0) + 1
        )

    return partner_clicks


def _aggregate_ab_group_clicks(
    events: list[dict[str, Any]],
) -> dict[str, int]:
    ab_group_clicks: dict[str, int] = {}

    for event in events:
        if not isinstance(event, dict):
            continue

        ab_group = str(event.get("ab_group", "")).strip() or "unknown"
        partner_id = str(event.get("partner_id", "")).strip()
        if not partner_id:
            continue

        ab_group_clicks[ab_group] = ab_group_clicks.get(ab_group, 0) + 1

    return ab_group_clicks


def _aggregate_click_users(
    events: list[dict[str, Any]],
) -> set[str]:
    click_users: set[str] = set()

    for event in events:
        if not isinstance(event, dict):
            continue

        user_key = str(event.get("user_key", "")).strip()
        partner_id = str(event.get("partner_id", "")).strip()
        if user_key and partner_id:
            click_users.add(user_key)

    return click_users


def _aggregate_link_stats(
    events: list[dict[str, Any]],
) -> tuple[int, int]:
    linked_clicks = 0
    unlinked_clicks = 0

    for event in events:
        if not isinstance(event, dict):
            continue

        partner_id = str(event.get("partner_id", "")).strip()
        if not partner_id:
            continue

        if str(event.get("impression_event_id", "")).strip():
            linked_clicks += 1
        else:
            unlinked_clicks += 1

    return linked_clicks, unlinked_clicks


def _aggregate_impressions(
    events: list[dict[str, Any]],
) -> tuple[
    dict[str, int],
    dict[str, int],
    set[str],
]:
    partner_impressions: dict[str, int] = {}
    ab_group_impressions: dict[str, int] = {}
    impression_users: set[str] = set()

    for event in events:
        if not isinstance(event, dict):
            continue

        user_key = str(event.get("user_key", "")).strip()
        ab_group = str(event.get("ab_group", "")).strip() or "unknown"
        partner_ids = event.get("partner_ids", [])
        if not user_key or not isinstance(partner_ids, list):
            continue

        impression_users.add(user_key)

        for partner_id in partner_ids:
            normalized_partner_id = str(partner_id or "").strip()
            if not normalized_partner_id:
                continue

            partner_impressions[normalized_partner_id] = (
                partner_impressions.get(normalized_partner_id, 0) + 1
            )
            ab_group_impressions[ab_group] = ab_group_impressions.get(ab_group, 0) + 1

    return (
        partner_impressions,
        ab_group_impressions,
        impression_users,
    )


def build_engagement_analytics_report() -> dict[str, Any]:
    try:
        events = read_partner_impressions()
        if not isinstance(events, list):
            events = []
    except Exception:
        events = []

    click_events = _read_all_click_events()
    partner_clicks = _aggregate_partner_clicks(click_events)
    ab_group_clicks = _aggregate_ab_group_clicks(click_events)
    click_users = _aggregate_click_users(click_events)
    linked_clicks, unlinked_clicks = _aggregate_link_stats(click_events)
    (
        partner_impressions,
        ab_group_impressions,
        impression_users,
    ) = _aggregate_impressions(events)

    all_partner_ids = set(partner_impressions.keys()) | set(partner_clicks.keys())
    partner_rows = [
        {
            "partner_id": partner_id,
            "impressions": partner_impressions.get(partner_id, 0),
            "clicks": partner_clicks.get(partner_id, 0),
            "ctr": _safe_ctr(
                partner_clicks.get(partner_id, 0),
                partner_impressions.get(partner_id, 0),
            ),
        }
        for partner_id in sorted(all_partner_ids)
    ]
    partner_rows.sort(
        key=lambda item: (
            -item["impressions"],
            -item["clicks"],
            str(item["partner_id"]),
        )
    )

    ranked_partners = sorted(
        partner_rows,
        key=lambda item: (
            -item["ctr"],
            -item["clicks"],
            -item["impressions"],
            str(item["partner_id"]),
        ),
    )

    all_ab_groups = set(ab_group_impressions.keys()) | set(ab_group_clicks.keys())
    ab_group_rows = [
        {
            "ab_group": ab_group,
            "impressions": ab_group_impressions.get(ab_group, 0),
            "clicks": ab_group_clicks.get(ab_group, 0),
            "ctr": _safe_ctr(
                ab_group_clicks.get(ab_group, 0),
                ab_group_impressions.get(ab_group, 0),
            ),
        }
        for ab_group in sorted(all_ab_groups)
    ]

    return {
        "summary": {
            "total_impressions": sum(partner_impressions.values()),
            "total_clicks": sum(partner_clicks.values()),
            "linked_clicks": linked_clicks,
            "unlinked_clicks": unlinked_clicks,
            "link_coverage": _safe_ctr(linked_clicks, sum(partner_clicks.values())),
            "unique_users": len(impression_users | click_users),
            "unique_partners": len(all_partner_ids),
            "limitations_note": V2_LIMITATIONS_NOTE,
        },
        "ab_groups": ab_group_rows,
        "partners": partner_rows,
        "top_partners": ranked_partners[:5],
        "bottom_partners": list(reversed(ranked_partners))[:5],
    }
