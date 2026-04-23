from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules import (
    CityEventSourceName,
    build_initial_health_entry,
    health_entry_to_dict,
)


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data"
SYSTEM_PATH = DATA_PATH / "system"
SOURCE_HEALTH_FILE = SYSTEM_PATH / "source_health.json"


def _build_initial_source_health() -> dict[str, Any]:
    return {
        "type": "source_health",
        "updated_at": None,
        "sources": {
            CityEventSourceName.ELECTRICITY.value: health_entry_to_dict(
                build_initial_health_entry(CityEventSourceName.ELECTRICITY)
            ),
            CityEventSourceName.WATER.value: health_entry_to_dict(
                build_initial_health_entry(CityEventSourceName.WATER)
            ),
            CityEventSourceName.PHARMACIES.value: health_entry_to_dict(
                build_initial_health_entry(CityEventSourceName.PHARMACIES)
            ),
        },
    }


def ensure_source_health_file() -> Path:
    SYSTEM_PATH.mkdir(parents=True, exist_ok=True)

    if not SOURCE_HEALTH_FILE.exists():
        initial_data = _build_initial_source_health()
        with SOURCE_HEALTH_FILE.open("w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

    return SOURCE_HEALTH_FILE


def load_source_health() -> dict[str, Any]:
    path = ensure_source_health_file()

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return _build_initial_source_health()

        if data.get("type") != "source_health":
            return _build_initial_source_health()

        sources = data.get("sources")
        if not isinstance(sources, dict):
            return _build_initial_source_health()

        return data

    except (json.JSONDecodeError, OSError):
        return _build_initial_source_health()


def get_source_health(source_name: str) -> dict[str, Any] | None:
    data = load_source_health()
    sources = data.get("sources", {})
    entry = sources.get(source_name)

    if not isinstance(entry, dict):
        return None

    return entry