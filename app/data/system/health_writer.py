from __future__ import annotations
import json
from pathlib import Path

HEALTH_FILE = Path("app/data/system/source_health.json")


def write_health(data: dict) -> None:
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if HEALTH_FILE.exists():
        try:
            existing = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    existing[data["source"]] = data
    HEALTH_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")