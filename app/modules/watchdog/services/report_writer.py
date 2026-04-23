from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
LATEST_REPORT_PATH = REPORTS_DIR / "watchdog_latest.json"


def _ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _write_report(path: Path, report: dict[str, Any]) -> Path:
    _ensure_reports_dir()
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def write_latest_report(report: dict[str, Any]) -> Path:
    return _write_report(LATEST_REPORT_PATH, report)


def write_timestamped_report(report: dict[str, Any]) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = REPORTS_DIR / f"watchdog_{timestamp}.json"
    return _write_report(path, report)

