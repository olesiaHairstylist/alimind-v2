from __future__ import annotations

from typing import TypedDict


class CityEventCard(TypedDict):
    id: str
    category: str
    title: str
    updated_at: str
    area: str
    status: str
    start_at: str
    end_at: str
    note: str
    source_name: str