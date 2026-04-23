from __future__ import annotations


def get_engagement_ab_group(user_key: str) -> str:
    normalized_user_key = str(user_key or "").strip()
    if not normalized_user_key:
        return "A"

    group_value = sum(ord(ch) for ch in normalized_user_key) % 2
    return "A" if group_value == 0 else "B"


def get_engagement_weight(user_key: str) -> float:
    try:
        group = get_engagement_ab_group(user_key)
    except Exception:
        return 0.0

    return 0.0 if group == "A" else 0.5
