from __future__ import annotations

from typing import TypedDict


class PartnerMatchContext(TypedDict, total=False):
    destination_airport: str
    lang: str
    route: str
    country_from: str
    country_to: str
    date: str
    user_key: str
    session_key: str
