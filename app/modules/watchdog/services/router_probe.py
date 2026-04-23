from __future__ import annotations

import importlib
from typing import Any

from aiogram import Router

from app.modules.watchdog.contracts.allowlist import (
    ALLOWED_ROUTER_MODULES,
    FORBIDDEN_MODULE_PATTERNS,
)


def _status_rank(status: str) -> int:
    return {"ok": 0, "warning": 1, "error": 2}.get(status, 2)


def _merge_status(current: str, new: str) -> str:
    return new if _status_rank(new) > _status_rank(current) else current


def _make_finding(status: str, code: str, message: str, **extra: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "status": status,
        "code": code,
        "message": message,
    }
    finding.update(extra)
    return finding


def _is_forbidden(module_name: str) -> bool:
    return any(pattern in module_name for pattern in FORBIDDEN_MODULE_PATTERNS)


def _find_router(module: Any) -> Router | None:
    for value in vars(module).values():
        if isinstance(value, Router):
            return value
    return None


def _count_handlers(router: Router) -> int | None:
    observers = getattr(router, "observers", None)
    if not isinstance(observers, dict):
        return None

    count = 0
    for observer in observers.values():
        handlers = getattr(observer, "handlers", None)
        if isinstance(handlers, list):
            count += len(handlers)
    return count


def probe_router_modules() -> dict[str, Any]:
    status = "ok"
    findings: list[dict[str, Any]] = []
    modules_summary: list[dict[str, Any]] = []

    for module_name in ALLOWED_ROUTER_MODULES:
        entry: dict[str, Any] = {
            "module": module_name,
            "import_status": "ok",
            "router_found": False,
            "handlers_count": None,
            "error": None,
        }

        if _is_forbidden(module_name):
            entry["import_status"] = "error"
            entry["error"] = "module matches forbidden pattern"
            modules_summary.append(entry)
            findings.append(
                _make_finding(
                    "error",
                    "router_module_forbidden",
                    "Allowed router module matches forbidden pattern.",
                    module=module_name,
                )
            )
            status = _merge_status(status, "error")
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            entry["import_status"] = "error"
            entry["error"] = str(exc)
            modules_summary.append(entry)
            findings.append(
                _make_finding(
                    "error",
                    "router_import_failed",
                    "Router module import failed.",
                    module=module_name,
                    error=str(exc),
                )
            )
            status = _merge_status(status, "error")
            continue

        router = _find_router(module)
        if router is None:
            entry["import_status"] = "warning"
            entry["error"] = "Router instance not found"
            modules_summary.append(entry)
            findings.append(
                _make_finding(
                    "warning",
                    "router_missing",
                    "Module imported but Router instance was not found.",
                    module=module_name,
                )
            )
            status = _merge_status(status, "warning")
            continue

        entry["router_found"] = True
        entry["handlers_count"] = _count_handlers(router)
        modules_summary.append(entry)

    return {
        "status": status,
        "findings": findings,
        "details": {
            "modules": modules_summary,
        },
    }

