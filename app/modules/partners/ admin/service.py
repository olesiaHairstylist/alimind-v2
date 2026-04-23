from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DATA_PATH = Path("app/data/objects")

ALLOWED_UPDATE_FIELDS = {
    "title",
    "description_short",
    "description_full",
    "location",
    "contact",
    "languages",
    "is_partner",
}


def apply_partner_field_update(obj: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
    if field not in ALLOWED_UPDATE_FIELDS:
        raise ValueError(f"Field not allowed: {field}")

    updated = deepcopy(obj)
    updated[field] = value
    return updated


def fetch_partner_by_id(partner_id: str) -> dict | None:
    if not partner_id:
        return None

    if not DATA_PATH.exists():
        return None

    for path in DATA_PATH.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        current_id = str(data.get("id", "")).strip()
        if current_id == partner_id:
            return data

    return None


def save_partner_object(obj: dict) -> dict:
    partner_id = str(obj.get("id", "")).strip()

    if not partner_id:
        return {
            "ok": False,
            "status_code": 400,
            "text": "Missing object id",
        }

    if not DATA_PATH.exists():
        DATA_PATH.mkdir(parents=True, exist_ok=True)

    path = DATA_PATH / f"{partner_id}.json"

    try:
        path.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        return {
            "ok": False,
            "status_code": 500,
            "text": f"Write failed: {e}",
        }

    return {
        "ok": True,
        "status_code": 200,
        "text": "Saved locally",
    }


def send_partner_to_api(obj: dict) -> dict:
    return save_partner_object(obj)