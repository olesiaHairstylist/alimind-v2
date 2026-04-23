from __future__ import annotations

import json
from pathlib import Path


OBJECTS_DIR = Path("app/data/objects")
PUBLIC_DIR = Path("app/data/public")
PUBLIC_FILE = PUBLIC_DIR / "partners.json"


def export_partners_public() -> Path:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []

    for path in sorted(OBJECTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        if not data.get("is_partner"):
            continue

        items.append(data)

    PUBLIC_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return PUBLIC_FILE