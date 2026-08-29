from __future__ import annotations

import re
import unicodedata
from typing import Any


# Public contract shared by Telegram deep links and the pharmacy UI.
# Codes are stable system identifiers; aliases reflect source values.
PHARMACY_DISTRICTS: dict[str, dict[str, Any]] = {
    "alanya_merkez": {
        "label": "Alanya Merkez",
        "aliases": ("ALANYA MERKEZ", "MERKEZ"),
    },
    "oba": {"label": "Oba", "aliases": ("OBA",)},
    "mahmutlar": {"label": "Mahmutlar", "aliases": ("MAHMUTLAR",)},
    "kestel": {"label": "Kestel", "aliases": ("KESTEL",)},
    "tosmur": {"label": "Tosmur", "aliases": ("TOSMUR",)},
    "konakli": {"label": "Konaklı", "aliases": ("KONAKLI",)},
    "avsallar": {"label": "Avsallar", "aliases": ("AVSALLAR",)},
    "cikcilli": {"label": "Çıkçıllı", "aliases": ("ÇIKÇILLI", "CIKCILLI")},
    "kadipasa": {"label": "Kadipaşa", "aliases": ("KADIPAŞA", "KADIPASA")},
    "saray": {"label": "Saray", "aliases": ("SARAY",)},
    "kale": {"label": "Kale", "aliases": ("KALE",)},
}


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def district_label(code: str) -> str | None:
    district = PHARMACY_DISTRICTS.get(code)
    return str(district["label"]) if district else None


def item_district_code(item: dict[str, Any]) -> str | None:
    # The source may group Oba/Cikcilli/etc. under broad `ALANYA MERKEZ`.
    # A district present in the address is therefore more precise. The source
    # region in details remains the fallback for addresses without a district.
    for value in (item.get("address", ""), item.get("details", "")):
        normalized_value = _normalize(value)
        for code, district in PHARMACY_DISTRICTS.items():
            for alias in district["aliases"]:
                pattern = rf"(?:^|\s){re.escape(_normalize(alias))}(?:\s|$)"
                if re.search(pattern, normalized_value):
                    return code
    return None


def filter_pharmacies(
    items: list[dict[str, Any]], district_code: str
) -> list[dict[str, Any]]:
    if district_code == "all":
        return items
    if district_code not in PHARMACY_DISTRICTS:
        return []
    return [item for item in items if item_district_code(item) == district_code]
