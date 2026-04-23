from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules import (
    SourceHealthEntry,
    health_entry_to_dict,
)
from .health_reader import (
    SOURCE_HEALTH_FILE,
    SYSTEM_PATH,
    load_source_health,
)


def save_source_health(data: dict[str, Any]) -> Path:
    SYSTEM_PATH.mkdir(parents=True, exist_ok=True)

    with SOURCE_HEALTH_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return SOURCE_HEALTH_FILE


def update_source_health_entry(source_name: str, entry: dict[str, Any] | SourceHealthEntry) -> Path:
    data = load_source_health()

    if "sources" not in data or not isinstance(data["sources"], dict):
        data["sources"] = {}

    if isinstance(entry, SourceHealthEntry):
        entry_data = health_entry_to_dict(entry)
    else:
        entry_data = entry

    data["sources"][source_name] = entry_data
    return save_source_health(data)


def set_source_health_updated_at(updated_at: str | None) -> Path:
    data = load_source_health()
    data["updated_at"] = updated_at
    return save_source_health(data)


def merge_source_health_entry(source_name: str, patch: dict[str, Any]) -> Path:
    data = load_source_health()

    if "sources" not in data or not isinstance(data["sources"], dict):
        data["sources"] = {}

    current = data["sources"].get(source_name, {})
    if not isinstance(current, dict):
        current = {}

    current.update(patch)
    data["sources"][source_name] = current

    return save_source_health(data)