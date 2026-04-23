from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.modules.watchdog.alerts import send_alert
from app.modules.watchdog.contracts import (
    CITY_EVENT_FILES,
    EXPECTED_EMPTY,
    GROUPED_STALE_WARNING_KEY,
    MODULE_LABELS,
)
from app.modules.watchdog.health import run_health_check
from app.modules.watchdog.logger import log_error, log_info, log_warn
from app.modules.watchdog.rules import evaluate
from app.modules.watchdog.snapshot import save_snapshot
from app.modules.watchdog.state import save_alert, should_alert


def _extract_module(issue_id: str) -> str:
    if issue_id.startswith("watchdog_"):
        return "watchdog"

    for module in CITY_EVENT_FILES:
        if issue_id.startswith(f"{module}_"):
            return module

    return "watchdog"


def _module_label(module: str) -> str:
    return MODULE_LABELS.get(module, module)


def _classify_issue_kind(issue_id: str) -> str:
    if issue_id.startswith("watchdog_"):
        return "internal_watchdog_error"
    if issue_id.endswith("_stale"):
        return "stale_data"
    if issue_id.endswith("_missing_file") or issue_id.endswith("_invalid_json") or issue_id.endswith("_updated_at_invalid"):
        return "data_error"
    if issue_id.endswith("_error"):
        return "system_error"
    if issue_id.endswith("_empty_unexpected"):
        return "unexpected_empty"
    if issue_id.endswith("_expected_empty"):
        return "expected_empty"
    return "system_error"


def _humanize_issue(issue_id: str) -> str:
    if issue_id.endswith("_missing_file"):
        return "файл данных отсутствует"
    if issue_id.endswith("_invalid_json"):
        return "JSON-файл данных поврежден"
    if issue_id.endswith("_error"):
        return "источник данных вернул ошибку"
    if issue_id.endswith("_updated_at_invalid"):
        return "некорректное время обновления"
    if issue_id.endswith("_stale"):
        return "данные устарели"
    if issue_id.endswith("_empty_unexpected"):
        return "получены пустые данные, хотя это не ожидается"
    if issue_id.endswith("_expected_empty"):
        return "пустые данные ожидаемы"
    if issue_id == "watchdog_evaluate_failed":
        return "watchdog не смог проверить правила состояния"
    if issue_id == "watchdog_run_failed":
        return "watchdog завершился с внутренней ошибкой"
    return f"обнаружена проблема: {issue_id}"


def _normalize_issue(issue: dict[str, str]) -> dict[str, str]:
    issue_id = str(issue.get("id", "unknown_issue"))
    kind = _classify_issue_kind(issue_id)
    level = str(issue.get("level", "warning"))

    if kind == "expected_empty":
        level = "info"

    return {
        "id": issue_id,
        "level": level,
        "kind": kind,
        "module": _extract_module(issue_id),
        "human_text": _humanize_issue(issue_id),
    }


def _build_expected_empty_issue(module: str) -> dict[str, str]:
    return {
        "id": f"{module}_expected_empty",
        "level": "info",
        "kind": "expected_empty",
        "module": module,
        "human_text": "пустые данные ожидаемы",
    }


def _compute_health_score(issues: list[dict[str, str]]) -> int:
    score = 100

    for issue in issues:
        if issue.get("level") == "critical":
            score -= 30
        elif issue.get("level") == "warning":
            score -= 10

    return max(score, 0)


def _build_snapshot(
    health_snapshot: dict[str, str],
    issues: list[dict[str, str]],
    alerts_sent: list[str],
) -> dict[str, Any]:
    modules = {
        module: health_snapshot.get(module, "error")
        for module in CITY_EVENT_FILES
    }

    status = "ok"
    if any(issue.get("level") == "critical" for issue in issues):
        status = "error"
    elif any(issue.get("level") == "warning" for issue in issues):
        status = "warning"

    return {
        "timestamp": health_snapshot.get("timestamp", ""),
        "status": status,
        "health_score": _compute_health_score(issues),
        "modules": modules,
        "issues": issues,
        "alerts_sent": alerts_sent,
        "health": health_snapshot,
    }


def _build_critical_alert_text(issue: dict[str, str]) -> str:
    return (
        "❗ WATCHDOG\n"
        f"Модуль: {_module_label(issue['module'])}\n"
        f"Проблема: {issue['human_text']}"
    )


def _build_warning_alert_text(issue: dict[str, str]) -> str:
    return (
        "⚠️ WATCHDOG\n"
        f"Модуль: {_module_label(issue['module'])}\n"
        f"Проблема: {issue['human_text']}"
    )


def _build_grouped_stale_alert_text(issues: list[dict[str, str]]) -> str:
    lines = ["⚠️ WATCHDOG", "Проблемы в нескольких модулях:"]

    for issue in issues:
        lines.append(f"- {_module_label(issue['module'])}: {issue['human_text']}")

    return "\n".join(lines)


def _build_grouped_module_warning_text(module: str, issues: list[dict[str, str]]) -> str:
    lines = ["⚠️ WATCHDOG", f"Проблемы в модуле {_module_label(module)}:"]

    for issue in issues:
        lines.append(f"- {issue['human_text']}")

    return "\n".join(lines)


async def run_watchdog(bot: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "ok",
        "snapshot": {},
        "issues": [],
        "alerts_sent": [],
    }

    try:
        health_snapshot = run_health_check()

        try:
            raw_issues = evaluate(health_snapshot)
        except Exception as exc:
            raw_issues = [{"id": "watchdog_evaluate_failed", "level": "critical"}]
            log_error(f"watchdog evaluate error: {exc}")

        issues = [_normalize_issue(issue) for issue in raw_issues]

        for module in CITY_EVENT_FILES:
            if health_snapshot.get(module) == "empty" and EXPECTED_EMPTY.get(module, False):
                issues.append(_build_expected_empty_issue(module))

        result["issues"] = issues

        if any(issue.get("level") == "critical" for issue in issues):
            result["status"] = "error"
        elif any(issue.get("level") == "warning" for issue in issues):
            result["status"] = "warning"

        for issue in issues:
            if issue.get("kind") == "expected_empty":
                try:
                    log_info(f"watchdog expected empty skipped: module={issue['module']}")
                except Exception as exc:
                    log_error(f"watchdog expected empty log error: {exc}; module={issue['module']}")

        critical_issues = [issue for issue in issues if issue.get("level") == "critical"]
        warning_issues = [
            issue for issue in issues
            if issue.get("level") == "warning" and issue.get("kind") != "expected_empty"
        ]

        stale_warning_issues = [issue for issue in warning_issues if issue.get("kind") == "stale_data"]
        grouped_stale_enabled = len(stale_warning_issues) > 1

        if grouped_stale_enabled:
            try:
                log_warn(
                    "watchdog grouped stale warning detected: "
                    + ", ".join(issue["module"] for issue in stale_warning_issues)
                )
                if should_alert(GROUPED_STALE_WARNING_KEY):
                    await send_alert(bot, _build_grouped_stale_alert_text(stale_warning_issues))
                    save_alert(GROUPED_STALE_WARNING_KEY)
                    result["alerts_sent"].append(GROUPED_STALE_WARNING_KEY)
                    log_warn("watchdog grouped stale warning sent")
            except Exception as exc:
                log_error(f"watchdog grouped stale alert error: {exc}")

        consumed_warning_ids = (
            {issue["id"] for issue in stale_warning_issues}
            if grouped_stale_enabled
            else set()
        )

        remaining_warning_issues = [
            issue for issue in warning_issues
            if issue["id"] not in consumed_warning_ids
        ]

        warning_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for issue in remaining_warning_issues:
            warning_groups[issue["module"]].append(issue)

        for issue in critical_issues:
            issue_id = issue["id"]
            try:
                log_error(f"watchdog critical issue detected: {issue_id}")
                if should_alert(issue_id):
                    await send_alert(bot, _build_critical_alert_text(issue))
                    save_alert(issue_id)
                    result["alerts_sent"].append(issue_id)
            except Exception as exc:
                log_error(f"watchdog critical alert pipeline error: {exc}; issue={issue_id}")

        for module, module_issues in warning_groups.items():
            if len(module_issues) > 1:
                group_key = f"grouped_warning_{module}"
                try:
                    log_warn(f"watchdog grouped warning detected: module={module}")
                    if should_alert(group_key):
                        await send_alert(bot, _build_grouped_module_warning_text(module, module_issues))
                        save_alert(group_key)
                        result["alerts_sent"].append(group_key)
                        log_warn(f"watchdog grouped warning sent: module={module}")
                except Exception as exc:
                    log_error(f"watchdog grouped module alert error: {exc}; module={module}")
                continue

            issue = module_issues[0]
            issue_id = issue["id"]
            try:
                log_warn(f"watchdog warning issue detected: {issue_id}")
                if should_alert(issue_id):
                    await send_alert(bot, _build_warning_alert_text(issue))
                    save_alert(issue_id)
                    result["alerts_sent"].append(issue_id)
            except Exception as exc:
                log_error(f"watchdog warning alert pipeline error: {exc}; issue={issue_id}")

        snapshot = _build_snapshot(health_snapshot, issues, result["alerts_sent"])
        result["snapshot"] = snapshot

        try:
            save_snapshot(snapshot)
        except Exception as exc:
            log_error(f"watchdog snapshot save error: {exc}")

        try:
            log_info(
                "watchdog summary: "
                f"status={result['status']} "
                f"health_score={snapshot['health_score']} "
                f"issues={len(result['issues'])} "
                f"alerts_sent={len(result['alerts_sent'])}"
            )
        except Exception:
            pass

        return result
    except Exception as exc:
        try:
            log_error(f"watchdog fatal error: {exc}")
        except Exception:
            pass
        result["status"] = "error"
        result["issues"] = [_normalize_issue({"id": "watchdog_run_failed", "level": "critical"})]
        result["snapshot"] = _build_snapshot(
            {"timestamp": "", **{module: "error" for module in CITY_EVENT_FILES}},
            result["issues"],
            result["alerts_sent"],
        )
        return result
