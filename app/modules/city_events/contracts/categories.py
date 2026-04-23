from __future__ import annotations

from enum import Enum


class CityEventCategory(str, Enum):
    PHARMACIES = "pharmacies"
    ELECTRICITY = "electricity"
    WATER = "water"
    EMERGENCY = "emergency"


ALL_CATEGORIES = [
    CityEventCategory.PHARMACIES,
    CityEventCategory.ELECTRICITY,
    CityEventCategory.WATER,
    CityEventCategory.EMERGENCY,
]