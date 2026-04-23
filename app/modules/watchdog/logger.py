from __future__ import annotations

import os
from datetime import datetime, timezone

from app.modules.watchdog.contracts import LOG_PATH

SILENT_MODE = os.getenv("SILENT_MODE", "false").strip().lower() == "true"


def _write(level: str, text: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = f"{datetime.now(timezone.utc).isoformat()} [{level}] {text}\n"
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        return


def log_info(text: str) -> None:
    if SILENT_MODE:
        return
    _write("INFO", text)


def log_warn(text: str) -> None:
    _write("WARN", text)


def log_error(text: str) -> None:
    _write("ERROR", text)


def log_event(text: str) -> None:
    log_info(text)
