from __future__ import annotations

from typing import Any


TITLE = "💊 Дежурные аптеки"


def _clean_text(value: str, limit: int = 95) -> str:
    value = (value or "").strip()

    if len(value) > limit:
        value = value[:limit].rsplit(" ", 1)[0] + "..."

    return value


def _extract_district(address: str) -> str:
    if not address:
        return ""

    lower = address.lower()

    districts = {
        "mahmutlar": "Mahmutlar",
        "oba": "Oba",
        "kadipaşa": "Kadipaşa",
        "kadipasa": "Kadipaşa",
        "kale": "Kale",
        "saray": "Saray",
        "cikcilli": "Cikcilli",
        "tosmur": "Tosmur",
        "kestel": "Kestel",
        "konaklı": "Konaklı",
        "konakli": "Konaklı",
        "avsallar": "Avsallar",
    }

    for key, label in districts.items():
        if key in lower:
            return label

    return ""


def render_pharmacies(payload: dict[str, Any], lang: str = "ru") -> str:
    if not payload:
        return f"{TITLE}\n\nНет данных"

    status = payload.get("status")
    items = payload.get("items") or []

    if status == "empty":
        return f"{TITLE}\n\nСегодня данных нет"

    lines: list[str] = [TITLE, ""]

    for idx, item in enumerate(items, start=1):
        title = _clean_text(item.get("title", ""), 60)
        details = _clean_text(item.get("details", ""), 95)
        address = _clean_text(item.get("address", ""), 95)
        phone = item.get("phone", "")

        district = _extract_district(address)

        lines.append(f"{idx}) {title}")

        if district:
            lines.append(f"📍 Район: {district}")

        if address:
            lines.append(f"🏠 Адрес: {address}")

        if details:
            lines.append(f"🧭 Как найти: {details}")

        if phone:
            lines.append(f"📞 {phone}")

        lines.append("")

    return "\n".join(lines).strip()