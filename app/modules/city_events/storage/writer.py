from __future__ import annotations

import json
from pathlib import Path

from app.modules.city_events.contracts.categories import CityEventCategory
from app.modules.city_events.storage.schema import CityEventPayload, payload_to_dict


CATEGORY_FILE_MAP: dict[CityEventCategory, str] = {
    CityEventCategory.PHARMACIES: "duty_pharmacies.json",
    CityEventCategory.ELECTRICITY: "electricity_outages.json",
    CityEventCategory.WATER: "water_outages.json",
    CityEventCategory.EMERGENCY: "emergency_contacts.json",
}


def get_category_storage_path(data_dir: Path, category: CityEventCategory) -> Path:
    filename = CATEGORY_FILE_MAP[category]
    return data_dir / filename


def write_payload(data_dir: Path, payload: CityEventPayload) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = get_category_storage_path(data_dir, payload.category)
    data = payload_to_dict(payload)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path