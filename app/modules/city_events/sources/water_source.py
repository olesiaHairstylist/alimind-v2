from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from app.data.system.source_health_contracts import (
    health_ok,
    health_expected_empty,
    health_error,
    ErrorCode,
)
from app.data.system.health_writer import write_health


APP_DIR = Path(__file__).resolve().parents[3]
RAW_FILE = APP_DIR / "data" / "sources" / "water_raw.json"

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")


def now_tr_iso() -> str:
    return datetime.now(ISTANBUL_TZ).isoformat()


def fetch_raw_data() -> list[dict]:
    """
    ВРЕМЕННО:
    сюда потом вставим реальный запрос к ASAT.
    Пока читает существующий raw, если он уже есть.
    """
    if not RAW_FILE.exists():
        return []

    text = RAW_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []

    data = json.loads(text)
    return data if isinstance(data, list) else []


def save_raw(data: list[dict]) -> Path:
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return RAW_FILE


def write_water_health(items: list[dict]) -> None:
    if items:
        write_health(
            health_ok(
                source_name="water",
                items_count=len(items),
                updated_at=now_tr_iso(),
            )
        )
    else:
        write_health(
            health_expected_empty(
                source_name="water",
                updated_at=now_tr_iso(),
            )
        )


def write_water_health_error(error: Exception) -> None:
    write_health(
        health_error(
            source_name="water",
            error_code=ErrorCode.FETCH_FAILED,
            error_details=str(error),
        )
    )


def run_fetch() -> Path:
    try:
        data = fetch_raw_data()
        print("FETCHED:", len(data))

        path = save_raw(data)
        write_water_health(data)

        return path

    except Exception as e:
        write_water_health_error(e)
        print("FETCH ERROR:", e)
        raise


if __name__ == "__main__":
    path = run_fetch()
    print("RAW SAVED:", path)
    print("ABS:", path.resolve())