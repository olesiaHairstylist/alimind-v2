from __future__ import annotations

from typing import Any
from datetime import datetime


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_electricity_payload() -> dict[str, Any]:
    """
    ВРЕМЕННЫЙ СТАБ (V3 SAFE)

    НЕ ломает систему
    НЕ тянет source
    НЕ падает

    Используется для восстановления pipeline
    """

    return {
        "category": "electricity",
        "updated_at": _now_iso(),
        "status": "empty",
        "items": [],
    }