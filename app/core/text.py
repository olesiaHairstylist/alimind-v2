from __future__ import annotations


def get_text(value, lang: str = "ru") -> str:
    if isinstance(value, dict):
        return value.get(lang) or value.get("ru") or ""
    return value or ""
