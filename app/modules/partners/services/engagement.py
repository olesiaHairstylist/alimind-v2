from __future__ import annotations

from app.modules.partners.storage.engagement_memory import mark_partner_click


def mark_click(user_key: str, partner_id: str) -> bool:
    return mark_partner_click(user_key=user_key, partner_id=partner_id)

