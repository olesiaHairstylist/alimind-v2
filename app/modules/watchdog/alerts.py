from __future__ import annotations

import os
from typing import Any

from app.modules.watchdog.logger import log_error, log_warn

ENV = os.getenv("ENV", "prod")


async def send_alert(bot: Any, text: str) -> None:
    if ENV == "local":
        return

    try:
        admin_id_raw = os.getenv("ADMIN_ID")
        admin_id = int(admin_id_raw) if admin_id_raw and admin_id_raw.isdigit() else None

        if bot is None or admin_id is None:
            log_warn(f"watchdog alert fallback: {text}")
            return

        await bot.send_message(admin_id, text)
    except Exception as exc:
        log_error(f"watchdog alert failed: {exc}; text={text}")
