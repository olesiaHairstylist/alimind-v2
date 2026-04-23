from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.modules.admin.access import is_admin_user
from app.modules.partners.services.click_signal_adaptive_explainability import (
    explain_adaptive_click_signal_weight,
)
from app.modules.partners.services.click_signal_explainability_guard import (
    explain_click_signal,
)
from app.modules.partners.services.click_signal_freshness_explainability import (
    explain_click_signal_freshness,
)
from app.modules.partners.services.click_signal_quality_explainability import (
    explain_click_signal_quality,
)

router = Router()


def _extract_partner_id(message: Message) -> str:
    text = str(message.text or "").strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return ""
    return str(parts[1]).strip()


def _bool_label(value: bool) -> str:
    return "yes" if value else "no"


def _optional_text(value: object, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text or fallback


def _render_click_signal_text(partner_id: str) -> str:
    explanation = explain_click_signal(partner_id)
    quality = explain_click_signal_quality(partner_id)
    freshness = explain_click_signal_freshness(partner_id)
    adaptive = explain_adaptive_click_signal_weight()
    return "\n".join(
        [
            f"Partner: {explanation['partner_id'] or '-'}",
            f"Guarded signal: {float(explanation['guarded_signal']):.2f}",
            f"Weighted signal: {float(explanation['weighted_signal']):.2f}",
            f"Has signal: {_bool_label(bool(explanation['has_signal']))}",
            f"Zero effect: {_bool_label(bool(explanation['is_zero_effect']))}",
            f"Capped: {_bool_label(bool(explanation['is_capped']))}",
            f"Weight: {float(explanation['weight']):.2f}",
            f"Max effect: {float(explanation['max_effect']):.2f}",
            "",
            "Quality:",
            f"Raw clicks: {int(quality['raw_clicks'])}",
            f"Min usable clicks: {int(quality['min_usable_clicks'])}",
            f"Usable: {_bool_label(bool(quality['usable']))}",
            f"Reason: {quality['reason']}",
            f"Gated signal: {float(quality['gated_signal']):.2f}",
            "",
            "Freshness:",
            f"Last clicked at: {_optional_text(freshness['last_clicked_at'])}",
            f"Signal age seconds: {_optional_text(freshness['signal_age_seconds'])}",
            f"Freshness state: {freshness['freshness_state']}",
            "",
            "Adaptive:",
            f"Base weight: {float(adaptive['base_weight']):.2f}",
            f"Adaptive multiplier: {float(adaptive['adaptive_multiplier']):.2f}",
            f"Effective weight: {float(adaptive['effective_weight']):.2f}",
            f"Adaptive dampened: {_bool_label(bool(adaptive['is_dampened']))}",
            f"Adaptive disabled: {_bool_label(bool(adaptive['is_disabled']))}",
            f"Adaptive reason: {adaptive['reason']}",
        ]
    )


@router.message(Command("click_signal"))
async def click_signal_handler(message: Message) -> None:
    user = message.from_user
    if not user or not is_admin_user(user.id):
        return

    partner_id = _extract_partner_id(message)
    await message.answer(_render_click_signal_text(partner_id))
