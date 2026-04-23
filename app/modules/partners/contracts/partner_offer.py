from __future__ import annotations

from typing import TypedDict


class PartnerOffer(TypedDict):
    id: str
    category: str
    subcategory: str
    status: str
    is_partner: bool
    offer_title: str
    offer_text: str
    action_type: str
    action_value: str
    priority: int

