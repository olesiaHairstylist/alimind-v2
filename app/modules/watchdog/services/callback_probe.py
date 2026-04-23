from __future__ import annotations

import importlib
import inspect
from types import ModuleType
from typing import Any, Callable


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


def _import_module(module_name: str) -> tuple[ModuleType | None, str | None]:
    try:
        return importlib.import_module(module_name), None
    except Exception as exc:
        return None, str(exc)


def _module_source(module: ModuleType) -> str:
    try:
        return inspect.getsource(module)
    except OSError:
        return ""


def _function_has_callback_answer(func: Callable[..., Any]) -> bool:
    try:
        source = inspect.getsource(func)
    except OSError:
        return False
    return "callback.answer(" in source


def probe_directory_callbacks() -> dict[str, Any]:
    status = "ok"
    findings: list[dict[str, Any]] = []

    callbacks_module, callbacks_error = _import_module("app.modules.directory.contracts.callbacks")
    menu_module, menu_error = _import_module("app.modules.directory.handlers.menu")
    category_module, category_error = _import_module("app.modules.directory.handlers.category")
    subcategory_module, subcategory_error = _import_module("app.modules.directory.handlers.subcategory")
    object_module, object_error = _import_module("app.modules.directory.handlers.object")

    imports = {
        "callbacks": callbacks_error,
        "menu": menu_error,
        "category": category_error,
        "subcategory": subcategory_error,
        "object": object_error,
    }

    for name, error in imports.items():
        if error:
            findings.append(
                _make_finding(
                    "error",
                    "directory_callback_import_failed",
                    "Directory callback probe import failed.",
                    module=name,
                    error=error,
                )
            )
            status = _merge_status(status, "error")

    if not all(module is not None for module in (callbacks_module, menu_module, category_module, subcategory_module, object_module)):
        return {
            "status": status,
            "findings": findings,
            "details": {
                "imports": imports,
            },
        }

    callback_checks = {
        "DIRECTORY_MENU_CB": hasattr(callbacks_module, "DIRECTORY_MENU_CB"),
        "build_directory_category_cb": hasattr(callbacks_module, "build_directory_category_cb"),
        "build_directory_subcategory_cb": hasattr(callbacks_module, "build_directory_subcategory_cb"),
        "build_directory_open_cb": hasattr(callbacks_module, "build_directory_open_cb"),
    }

    for name, exists in callback_checks.items():
        if not exists:
            findings.append(
                _make_finding(
                    "error",
                    "directory_callback_missing",
                    "Expected directory callback contract is missing.",
                    contract=name,
                )
            )
            status = _merge_status(status, "error")

    menu_source = _module_source(menu_module)
    category_source = _module_source(category_module)
    subcategory_source = _module_source(subcategory_module)
    object_source = _module_source(object_module)

    if "DIRECTORY_MENU_CB" not in menu_source:
        findings.append(
            _make_finding(
                "warning",
                "directory_menu_handler_mismatch",
                "Directory menu handler module does not reference DIRECTORY_MENU_CB.",
                module="app.modules.directory.handlers.menu",
            )
        )
        status = _merge_status(status, "warning")

    if "is_directory_category_cb" not in category_source:
        findings.append(
            _make_finding(
                "warning",
                "directory_category_handler_mismatch",
                "Directory category handler module does not reference category callback matcher.",
                module="app.modules.directory.handlers.category",
            )
        )
        status = _merge_status(status, "warning")

    if "is_directory_subcategory_cb" not in subcategory_source:
        findings.append(
            _make_finding(
                "warning",
                "directory_subcategory_handler_mismatch",
                "Directory subcategory handler module does not reference subcategory callback matcher.",
                module="app.modules.directory.handlers.subcategory",
            )
        )
        status = _merge_status(status, "warning")

    if "is_directory_open_cb" not in object_source:
        findings.append(
            _make_finding(
                "warning",
                "directory_object_handler_mismatch",
                "Directory object handler module does not reference object callback matcher.",
                module="app.modules.directory.handlers.object",
            )
        )
        status = _merge_status(status, "warning")

    callback_handlers = [
        ("app.modules.directory.handlers.menu", getattr(menu_module, "open_directory_menu", None)),
        ("app.modules.directory.handlers.category", getattr(category_module, "open_directory_category", None)),
        ("app.modules.directory.handlers.subcategory", getattr(subcategory_module, "open_directory_subcategory", None)),
        ("app.modules.directory.handlers.object", getattr(object_module, "open_directory_object", None)),
    ]

    callback_answer_checks: list[dict[str, Any]] = []
    for module_name, func in callback_handlers:
        has_answer = callable(func) and _function_has_callback_answer(func)
        callback_answer_checks.append(
            {
                "module": module_name,
                "function": getattr(func, "__name__", None),
                "callback_answer_present": has_answer,
            }
        )
        if callable(func) and not has_answer:
            findings.append(
                _make_finding(
                    "warning",
                    "callback_answer_missing",
                    "Callback handler source does not contain callback.answer().",
                    module=module_name,
                    function=getattr(func, "__name__", None),
                )
            )
            status = _merge_status(status, "warning")

    return {
        "status": status,
        "findings": findings,
        "details": {
            "imports": imports,
            "callback_checks": callback_checks,
            "callback_answer_checks": callback_answer_checks,
        },
    }


def probe_city_events_callbacks() -> dict[str, Any]:
    status = "ok"
    findings: list[dict[str, Any]] = []

    callbacks_module, callbacks_error = _import_module("app.modules.city_events.ui.callbacks")
    router_module, router_error = _import_module("app.modules.city_events.ui.router")
    handlers_module, handlers_error = _import_module("app.modules.city_events.ui.handlers")
    start_module, start_error = _import_module("app.handlers.start")

    imports = {
        "callbacks": callbacks_error,
        "router": router_error,
        "handlers": handlers_error,
        "start": start_error,
    }

    for name, error in imports.items():
        if error:
            findings.append(
                _make_finding(
                    "error",
                    "city_events_callback_import_failed",
                    "City events callback probe import failed.",
                    module=name,
                    error=error,
                )
            )
            status = _merge_status(status, "error")

    if not all(module is not None for module in (callbacks_module, router_module, handlers_module, start_module)):
        return {
            "status": status,
            "findings": findings,
            "details": {
                "imports": imports,
            },
        }

    callback_checks = {
        "CITY_EVENTS_MENU_CB": hasattr(callbacks_module, "CITY_EVENTS_MENU_CB"),
        "CITY_EVENTS_BACK_CB": hasattr(callbacks_module, "CITY_EVENTS_BACK_CB"),
        "CITY_EVENTS_PHARMACIES_CB": hasattr(callbacks_module, "CITY_EVENTS_PHARMACIES_CB"),
        "CITY_EVENTS_ELECTRICITY_CB": hasattr(callbacks_module, "CITY_EVENTS_ELECTRICITY_CB"),
        "CITY_EVENTS_WATER_CB": hasattr(callbacks_module, "CITY_EVENTS_WATER_CB"),
        "CITY_EVENTS_EMERGENCY_CB": hasattr(callbacks_module, "CITY_EVENTS_EMERGENCY_CB"),
    }

    for name, exists in callback_checks.items():
        if not exists:
            findings.append(
                _make_finding(
                    "error",
                    "city_events_callback_missing",
                    "Expected city events callback contract is missing.",
                    contract=name,
                )
            )
            status = _merge_status(status, "error")

    router_source = _module_source(router_module)
    for name in callback_checks:
        if callback_checks[name] and name not in router_source:
            findings.append(
                _make_finding(
                    "warning",
                    "city_events_handler_mismatch",
                    "City events router does not reference expected callback constant.",
                    contract=name,
                    module="app.modules.city_events.ui.router",
                )
            )
            status = _merge_status(status, "warning")

    callback_handlers = [
        ("app.modules.city_events.ui.handlers", getattr(handlers_module, "open_city_events_menu", None)),
        ("app.modules.city_events.ui.handlers", getattr(handlers_module, "open_pharmacies", None)),
        ("app.modules.city_events.ui.handlers", getattr(handlers_module, "open_electricity", None)),
        ("app.modules.city_events.ui.handlers", getattr(handlers_module, "open_water", None)),
        ("app.modules.city_events.ui.handlers", getattr(handlers_module, "open_emergency", None)),
    ]

    callback_answer_checks: list[dict[str, Any]] = []
    for module_name, func in callback_handlers:
        has_answer = callable(func) and _function_has_callback_answer(func)
        callback_answer_checks.append(
            {
                "module": module_name,
                "function": getattr(func, "__name__", None),
                "callback_answer_present": has_answer,
            }
        )
        if callable(func) and not has_answer:
            findings.append(
                _make_finding(
                    "warning",
                    "callback_answer_missing",
                    "Callback handler source does not contain callback.answer().",
                    module=module_name,
                    function=getattr(func, "__name__", None),
                )
            )
            status = _merge_status(status, "warning")

    start_source = _module_source(start_module)
    if "main:info" in start_source and 'c.data == "main:info"' not in start_source:
        findings.append(
            _make_finding(
                "warning",
                "button_handler_missing",
                "Button callback exists in main menu but matching handler was not found.",
                callback_data="main:info",
                module="app.handlers.start",
            )
        )
        status = _merge_status(status, "warning")

    return {
        "status": status,
        "findings": findings,
        "details": {
            "imports": imports,
            "callback_checks": callback_checks,
            "callback_answer_checks": callback_answer_checks,
        },
    }


def probe_callback_contracts() -> dict[str, Any]:
    directory_report = probe_directory_callbacks()
    city_events_report = probe_city_events_callbacks()
    status = "ok"
    for part in (directory_report["status"], city_events_report["status"]):
        status = _merge_status(status, part)

    findings = [
        *directory_report["findings"],
        *city_events_report["findings"],
    ]

    return {
        "status": status,
        "findings": findings,
        "details": {
            "directory": directory_report,
            "city_events": city_events_report,
        },
    }

