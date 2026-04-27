from __future__ import annotations

SEARCH_MAP = {
    "стрижка": ("beauty", "hair"),
    "волосы": ("beauty", "hair"),
    "парикмахер": ("beauty", "hair"),
    "окрашивание": ("beauty", "hair"),
    "блонд": ("beauty", "hair"),

    "маникюр": ("beauty", "nails"),
    "ногти": ("beauty", "nails"),

    "брови": ("beauty", "brows"),
}


def find_directory_target(text: str) -> tuple[str, str] | None:
    query = (text or "").lower()

    for keyword, target in SEARCH_MAP.items():
        if keyword in query:
            return target

    return None