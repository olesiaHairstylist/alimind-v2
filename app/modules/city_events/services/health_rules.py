from __future__ import annotations

from typing import Any


RULES: dict[str, dict[str, Any]] = {
    "electricity": {
        "empty_allowed": True,
        "empty_is_expected": True,
    },
    "water": {
        "empty_allowed": True,
        "empty_is_expected": True,
    },
    "pharmacies": {
        "empty_allowed": False,
        "empty_is_expected": False,
    },
    "emergency": {
        "empty_allowed": False,
        "empty_is_expected": False,
    },
}


def get_rule(category: str) -> dict[str, Any]:
    return RULES.get(
        category,
        {
            "empty_allowed": False,
            "empty_is_expected": False,
        },
    )