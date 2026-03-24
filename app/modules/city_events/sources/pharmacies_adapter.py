from typing import List, Dict, Any


def adapt_pharmacies_raw(raw_json: Dict[str, Any], source_region_id: str) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []

    items = raw_json.get("data", [])
    if not isinstance(items, list):
        return result

    for item in items:
        if not isinstance(item, dict):
            continue

        pharmacy_id = item.get("EczaneID")
        name = item.get("EczaneAdi")
        district = item.get("EczaneILCE")

        if not pharmacy_id or not name or not district:
            continue

        if "tanımlaması yapılmama" in district.lower():
            continue

        result.append({
            "source_region_id": source_region_id,
            "pharmacy_id": str(pharmacy_id).strip(),
            "name": str(name).strip(),
            "district": str(district).strip(),
        })

    return result