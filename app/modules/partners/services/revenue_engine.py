from __future__ import annotations
from app.modules.partners.services.engagement_analytics import build_engagement_analytics_report
from app.modules.partners.services.engagement_ranking import compute_scores_for_offers
from datetime import datetime, timezone
from typing import Any
from app.modules.partners.services.engagement_ranking import compute_scores_for_offers


from app.modules.partners.contracts.match_context import PartnerMatchContext
from app.modules.partners.contracts.partner_offer import PartnerOffer
from app.modules.partners.normalize.offers import normalize_partner_offers
from app.modules.partners.rules.eligibility import filter_eligible_partner_offers
from app.modules.partners.services.engagement_audit_trace import attach_audit_trace
from app.modules.partners.services.engagement_explainability import attach_explainability
from app.modules.partners.services.engagement_monetization import apply_monetization_signal
from app.modules.partners.services.engagement_operator_debug import attach_operator_debug_view
from app.modules.partners.services.engagement_quality_gates import apply_quality_gates
from app.modules.partners.services.engagement_scoring import apply_engagement_scoring
from app.modules.partners.services.engagement_token_boost import apply_token_boost
from app.modules.partners.services.engagement_weight_control import get_v3_preview_weight
from app.modules.partners.services.click_signal_freshness_modifier import (
    apply_freshness_modifier,
)
from app.modules.partners.services.click_signal_quality_gate import (
    get_quality_gated_click_signal,
)
from app.modules.partners.services.click_signal_weight_balance import (
    apply_freshness_weight_balance,
)
from app.modules.partners.services.click_signal_weight_control import (
    apply_click_signal_weight,
)
from app.modules.partners.source.reader import load_raw_partner_files
from app.modules.partners.storage.impressions_memory import mark_partner_impression
from app.modules.partners.storage.memory import get_seen_memory, mark_offers_shown
from app.modules.partners.storage.session_memory import (
    get_session_state,
    mark_session_shown,
)

FREQUENCY_CAP_SECONDS = 30 * 60
MAX_OFFERS = 2
TRANSFER_BOOST = 10
SEEN_COUNT_DECAY = 12
RECENT_DECAY = 8
SESSION_COUNT_PENALTY = 26
CONSECUTIVE_PENALTY = 34


def _get_user_key(context: PartnerMatchContext) -> str:
    return (
        str(context.get("user_key", "")).strip()
        or str(context.get("session_key", "")).strip()
        or "demo"
    )


def _get_session_key(context: PartnerMatchContext) -> str:
    return (
        str(context.get("session_key", "")).strip()
        or str(context.get("user_key", "")).strip()
        or "demo_session"
    )


def _get_route_airports(context: PartnerMatchContext) -> set[str]:
    route = str(context.get("route", "")).strip().upper()
    if not route:
        return set()

    return {part.strip() for part in route.split("-") if part.strip()}


def _parse_iso_datetime(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None

    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _was_shown_recently(last_shown_at: str) -> bool:
    shown_at = _parse_iso_datetime(last_shown_at)
    if shown_at is None:
        return False

    age_seconds = (datetime.now(timezone.utc) - shown_at).total_seconds()
    return age_seconds < FREQUENCY_CAP_SECONDS


def _get_effective_priority(offer: PartnerOffer, context: PartnerMatchContext) -> int:
    priority = int(offer["priority"])
    if offer["subcategory"] == "transfer" and str(context.get("destination_airport", "")).strip():
        priority += TRANSFER_BOOST
    if offer["subcategory"] == "esim" and (
        str(context.get("country_from", "")).strip().upper()
        and str(context.get("country_to", "")).strip().upper()
        and str(context.get("country_from", "")).strip().upper()
        != str(context.get("country_to", "")).strip().upper()
    ):
        priority += 6
    return priority


def _matches_geo(raw_offer: dict[str, Any], context: PartnerMatchContext) -> bool:
    country_from = str(context.get("country_from", "")).strip().upper()
    country_to = str(context.get("country_to", "")).strip().upper()
    destination_airport = str(context.get("destination_airport", "")).strip().upper()
    route_airports = _get_route_airports(context)
    if destination_airport:
        route_airports.add(destination_airport)

    route_scope = raw_offer.get("route_scope")
    geo_scope = str(raw_offer.get("geo_scope", "")).strip().lower()

    if geo_scope == "global":
        return True

    if not isinstance(route_scope, dict):
        return True

    countries = {
        str(item).strip().upper()
        for item in route_scope.get("countries", [])
        if str(item).strip()
    }
    if countries:
        requested_countries = {country_from, country_to} - {""}
        if requested_countries and requested_countries.isdisjoint(countries):
            return False

    airports = {
        str(item).strip().upper()
        for item in route_scope.get("airports", [])
        if str(item).strip()
    }
    if airports and route_airports and route_airports.isdisjoint(airports):
        return False

    return True


def _get_seen_decay(seen_info: dict[str, Any]) -> int:
    seen_count = int(seen_info.get("count", 0))
    decay = seen_count * SEEN_COUNT_DECAY
    if _was_shown_recently(str(seen_info.get("last_shown_at", ""))):
        decay += RECENT_DECAY
    return decay


def _rank_key(
    offer: PartnerOffer,
    context: PartnerMatchContext,
    session_state: dict[str, Any],
    seen_memory: dict[str, dict[str, Any]],
) -> tuple[int, int, int, int, int, float, str]:
    seen_info = seen_memory.get(offer["id"], {})
    seen_count = int(seen_info.get("count", 0))
    session_shown = set(session_state.get("shown", []))
    session_counts = session_state.get("counts", {})
    last_displayed = set(session_state.get("last_displayed", []))

    session_count = int(session_counts.get(offer["id"], 0))
    session_rank = 1 if offer["id"] in session_shown else 0
    user_rank = 1 if seen_count > 0 else 0
    seen_decay = _get_seen_decay(seen_info)
    session_decay = session_count * SESSION_COUNT_PENALTY
    consecutive_decay = CONSECUTIVE_PENALTY if offer["id"] in last_displayed else 0
    effective_priority = (
        _get_effective_priority(offer, context)
        - seen_decay
        - session_decay
        - consecutive_decay
    )
    partner_id = str(offer.get("id", ""))
    click_signal = get_quality_gated_click_signal(partner_id)
    click_signal = apply_freshness_modifier(partner_id, click_signal)
    click_guard = apply_click_signal_weight(
        click_signal
    )
    click_guard = apply_freshness_weight_balance(partner_id, click_guard)

    return (
        session_rank,
        user_rank,
        -effective_priority,
        session_count,
        seen_decay,
        -click_guard,
        str(offer["id"]),
    )


def _select_display_offers(
    offers: list[PartnerOffer],
    context: PartnerMatchContext,
    session_state: dict[str, Any],
    seen_memory: dict[str, dict[str, Any]],
) -> list[PartnerOffer]:
    ranked_offers = sorted(
        offers,
        key=lambda offer: _rank_key(offer, context, session_state, seen_memory),
    )

    selected: list[PartnerOffer] = []
    seen_subcategories: set[str] = set()

    for offer in ranked_offers:
        subcategory = offer["subcategory"]
        if subcategory in seen_subcategories:
            continue

        selected.append(offer)
        seen_subcategories.add(subcategory)

        if len(selected) >= MAX_OFFERS:
            break

    return selected


def _apply_v3_active_preview(final_offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not final_offers:
        return final_offers

    preview_weight = get_v3_preview_weight()
    if preview_weight <= 0:
        return final_offers

    return sorted(
        final_offers,
        key=lambda offer: (
            -(
                float(offer.get("priority", 0))
                + float(offer.get("_engagement_score", 0.0)) * preview_weight
                + float(offer.get("_token_boost", 0.0))
                + float(offer.get("_monetization_boost", 0.0))
            ),
            -int(offer.get("priority", 0)),
            str(offer.get("id", "")),
        ),
    )


def build_revenue_offers_result(
    context: PartnerMatchContext,
    has_ticket_result: bool,
) -> dict[str, Any]:
    raw_offers = load_raw_partner_files()
    matched_raw_offers = [
        raw_offer
        for raw_offer in raw_offers
        if isinstance(raw_offer, dict) and _matches_geo(raw_offer, context)
    ]
    normalized_offers = normalize_partner_offers(matched_raw_offers, str(context.get("lang", "en")))
    eligible_offers = filter_eligible_partner_offers(
        normalized_offers,
        context=context,
        has_ticket_result=has_ticket_result,
    )

    user_key = _get_user_key(context)
    session_key = _get_session_key(context)
    seen_memory = get_seen_memory(user_key)
    session_state = get_session_state(session_key)
    selected_offers = _select_display_offers(
        eligible_offers,
        context=context,
        session_state=session_state,
        seen_memory=seen_memory,
    )
    final_offers = apply_engagement_scoring(selected_offers, user_key)
    impression_event_id = ""
    # --- ENGAGEMENT_ENGINE_V3 PASSIVE MODE (no ranking impact) ---
    try:
        stats = {}
        tokens = {}

        final_offers = compute_scores_for_offers(
            offers=final_offers,
            stats=stats,
            tokens=tokens,
        )
    except Exception:
        pass

        # --- ENGAGEMENT_ENGINE_V3 PASSIVE MODE (no ranking impact) ---
        try:
            analytics_report = build_engagement_analytics_report()

            stats = {
                row["partner_id"]: {
                    "impressions": row.get("impressions", 0),
                    "clicks": row.get("clicks", 0),
                    "ctr": row.get("ctr", 0.0),
                }
                for row in analytics_report.get("partners", [])
                if isinstance(row, dict) and str(row.get("partner_id", "")).strip()
            }

            tokens = {}

            final_offers = compute_scores_for_offers(
                offers=final_offers,
                stats=stats,
                tokens=tokens,
            )
        except Exception:
            pass

        final_offers = compute_scores_for_offers(
            offers=final_offers,
            stats=stats,
            tokens=tokens,
        )
    except Exception:
        pass
    final_offers = apply_quality_gates(final_offers)
    final_offers = apply_token_boost(final_offers)
    final_offers = apply_monetization_signal(final_offers)
    final_offers = _apply_v3_active_preview(final_offers)
    final_offers = attach_explainability(final_offers)
    final_offers = attach_operator_debug_view(final_offers)
    final_offers = attach_audit_trace(final_offers)
    if final_offers:
        first_final_offer = final_offers[0]
        impression_event_id = mark_partner_impression(
            user_key=str(context.get("user_key", "")).strip(),
            session_key=str(context.get("session_key", "")).strip(),
            ab_group=str(first_final_offer.get("ab_group", "")).strip(),
            engagement_weight=float(first_final_offer.get("engagement_weight", 0.0)),
            partner_ids=[str(offer["id"]) for offer in final_offers if str(offer.get("id", "")).strip()],
        )
        mark_offers_shown(
            user_key=user_key,
            partner_ids=[offer["id"] for offer in final_offers],
        )
        mark_session_shown(
            session_key=session_key,
            partner_ids=[offer["id"] for offer in final_offers],
        )
    # --- DEBUG V3 SCORES ---
    try:
        print("\n[V3 DEBUG SCORES]")
        for offer in final_offers:
            print(
                str(offer.get("id")),
                "->",
                offer.get("_engagement_score")
            )
    except Exception:
        pass

    return {
        "user_key": user_key,
        "session_key": session_key,
        "context": context,
        "source_count": len(raw_offers),
        "normalized_count": len(normalized_offers),
        "eligible_count": len(eligible_offers),
        "offers": final_offers,
        "impression_event_id": impression_event_id,
    }
