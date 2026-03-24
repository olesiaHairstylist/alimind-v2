from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.modules.city_events.contracts.categories import ALL_CATEGORIES, CityEventCategory
from app.modules.city_events.storage.reader import read_payload
from app.modules.city_events.storage.schema import CityEventPayload


@dataclass(slots=True)
class FeedEntry:
    category: CityEventCategory
    payload: CityEventPayload | None


def build_city_events_feed(data_dir: Path) -> list[FeedEntry]:
    entries: list[FeedEntry] = []

    for category in ALL_CATEGORIES:
        payload = read_payload(data_dir, category)
        entries.append(FeedEntry(category=category, payload=payload))

    return entries