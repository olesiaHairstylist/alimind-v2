from __future__ import annotations

from typing import Any


TITLE = "🚨 Экстренные службы"


def render_emergency(payload: dict[str, Any]) -> str:
    if not payload:
        return f"{TITLE}\n\nНет данных"

    status = payload.get("status")
    items = payload.get("items") or []

    if status == "empty":
        return f"{TITLE}\n\nСегодня данных нет"

    lines: list[str] = [TITLE, ""]

    for idx, item in enumerate(items, start=1):
        title = str(item.get("title", "")).strip()
        details = str(item.get("details", "")).strip()
        phone = str(item.get("phone", "")).strip()

        lines.append(f"{idx}. {title}")

        if details:
            lines.append(details)

        if phone:
            lines.append(f"📞 {phone}")

        lines.append("")

    return "\n".join(lines).strip()