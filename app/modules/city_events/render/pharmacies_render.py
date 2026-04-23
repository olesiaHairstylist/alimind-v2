from __future__ import annotations

from typing import Any


TITLE = "💊 Дежурные аптеки"


def render_pharmacies(payload: dict[str, Any]) -> str:
    if not payload:
        return f"{TITLE}\n\nНет данных"

    status = payload.get("status")
    items = payload.get("items") or []

    if status == "empty":
        return f"{TITLE}\n\nСегодня данных нет"

    lines: list[str] = ["💊 Дежурные аптеки", ""]

    for idx, item in enumerate(items, start=1):
        title = item.get("title", "")
        details = item.get("details", "")
        address = item.get("address", "")
        phone = item.get("phone", "")

        lines.append(f"{idx}. {title}")

        if details:
            lines.append(f"{details}")

        if address:
            lines.append(f"📍 {address}")

        if phone:
            lines.append(f"📞 {phone}")

        lines.append("")  # отступ между карточками

    return "\n".join(lines).strip()