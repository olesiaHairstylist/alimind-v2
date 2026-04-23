from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.watchdog import WATCHDOG_VERSION
from app.modules.watchdog.services.callback_probe import probe_callback_contracts
from app.modules.watchdog.services.json_probe import probe_json_dirs, probe_object_files
from app.modules.watchdog.services.router_probe import probe_router_modules


def _status_rank(status: str) -> int:
    return {"ok": 0, "warning": 1, "error": 2}.get(status, 2)


def _merge_status(current: str, new: str) -> str:
    return new if _status_rank(new) > _status_rank(current) else current


def build_watchdog_report() -> dict[str, Any]:
    json_dirs_report = probe_json_dirs()
    object_files_report = probe_object_files()
    router_report = probe_router_modules()
    callback_report = probe_callback_contracts()

    overall_status = "ok"
    for part_status in (
        json_dirs_report["status"],
        object_files_report["status"],
        router_report["status"],
        callback_report["status"],
    ):
        overall_status = _merge_status(overall_status, part_status)

    findings = [
        *json_dirs_report["findings"],
        *object_files_report["findings"],
        *router_report["findings"],
        *callback_report["findings"],
    ]

    summary = {
        "json_dirs_status": json_dirs_report["status"],
        "object_files_status": object_files_report["status"],
        "router_modules_status": router_report["status"],
        "callback_contracts_status": callback_report["status"],
        "findings_count": len(findings),
    }

    return {
        "watchdog_version": WATCHDOG_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "summary": summary,
        "findings": findings,
        "details": {
            "json_dirs": json_dirs_report["details"],
            "object_files": object_files_report["details"],
            "router_modules": router_report["details"],
            "callback_contracts": callback_report["details"],
        },
    }

