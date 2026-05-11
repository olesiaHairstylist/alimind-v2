from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

EVENTS_PATH = Path("app/data/system/analytics_events.jsonl")


def log_event(event: dict) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    event["ts"] = datetime.utcnow().isoformat()

    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

_last_event = None


def log_event(event: dict) -> None:
    global _last_event

    if event == _last_event:
        return

    _last_event = event

    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    event["ts"] = datetime.utcnow().isoformat()

    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")