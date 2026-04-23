from __future__ import annotations

import os


def get_admin_user_id() -> int | None:
    raw = os.getenv("ADMIN_USER_ID")
    if not raw:
        return None

    try:
        return int(raw)
    except ValueError:
        return None


def is_admin_user(user_id: int) -> bool:
    admin_user_id = get_admin_user_id()
    if admin_user_id is None:
        return False

    return user_id == admin_user_id