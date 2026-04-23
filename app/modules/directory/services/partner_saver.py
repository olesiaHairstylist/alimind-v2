from __future__ import annotations
import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

DATA_PATH = Path("app/data/objects")

TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def generate_id(title: str) -> str:
    value = title.lower().strip()
    value = ''.join(TRANSLIT_MAP.get(ch, ch) for ch in value)
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_")

    base = value[:20].strip("_") or "partner"
    suffix = hashlib.md5(value.encode("utf-8")).hexdigest()[:6]

    return f"{base}_{suffix}"


def build_partner_payload(data: dict) -> dict:
    partner_id = str(data.get("id", "")).strip()

    if not partner_id:
        raise ValueError("Partner ID is missing in FSM data")

    payload = {
        "id": partner_id,
        "title": data["title"],
        "category": data["category"],
        "subcategory": data.get("subcategory", ""),
        "description_short": data["description_short"],
        "description_full": data["description_full"],
        "location": data["location"],
        "contact": data["contact"],
        "image_url": data.get("image_url", ""),
        "languages": ["ru"],
        "is_partner": True,
    }

    image_path = str(data.get("image_path", "")).strip()
    if image_path:
        payload["image_path"] = image_path

    return payload


def send_partner_to_wordpress(obj: dict) -> dict:
    url = os.getenv("ALIMIND_WP_PARTNERS_API_URL")
    token = os.getenv("ALIMIND_WP_API_TOKEN")

    if not url or not token:
        return {"ok": False, "error": "API config missing"}

    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-AliMind-Token": token,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {
                "ok": True,
                "status": resp.status,
                "response": resp.read().decode(),
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def save_local_json(payload: dict) -> Path:
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    partner_id = str(payload.get("id", "")).strip()
    if not partner_id:
        raise ValueError("Partner ID is missing in payload")

    file_path = DATA_PATH / f"{partner_id}.json"

    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return file_path


def save_partner(payload: dict) -> dict:
    path = save_local_json(payload)
    api_result = send_partner_to_wordpress(payload)

    if not api_result["ok"]:
        return {
            "ok": False,
            "path": str(path),
            "stage": "wordpress",
            "error": api_result.get("error"),
            "response": api_result.get("response", ""),
        }

    return {
        "ok": True,
        "path": str(path),
        "api": api_result,
    }
