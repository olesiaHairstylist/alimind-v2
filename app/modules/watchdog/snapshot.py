from __future__ import annotations

import json
from typing import Any

from app.modules.watchdog.contracts import SNAPSHOT_PATH


def save_snapshot(snapshot: dict[str, Any]) -> None:
    try:
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        return

