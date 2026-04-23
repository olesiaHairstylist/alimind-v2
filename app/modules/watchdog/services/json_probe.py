from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.modules.watchdog.contracts.allowlist import ALLOWED_JSON_DIRS

ROOT_DIR = Path(__file__).resolve().parents[4]
OBJECTS_DIR = ROOT_DIR / "app" / "data" / "objects"
REQUIRED_OBJECT_FIELDS: tuple[str, ...] = (
    "id",
    "title",
    "category",
    "subcategory",
    "description_short",
    "description_full",
    "location",
    "contact",
    "languages",
    "is_partner",
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


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def probe_json_dirs() -> dict[str, Any]:
    status = "ok"
    findings: list[dict[str, Any]] = []
    directories: list[dict[str, Any]] = []

    for raw_dir in ALLOWED_JSON_DIRS:
        path = ROOT_DIR / raw_dir
        entry: dict[str, Any] = {
            "path": raw_dir,
            "exists": path.exists(),
            "json_files_count": 0,
            "status": "ok",
        }

        if not path.exists() or not path.is_dir():
            entry["status"] = "error"
            entry["error"] = "directory missing"
            directories.append(entry)
            findings.append(
                _make_finding(
                    "error",
                    "json_dir_missing",
                    "Allowed JSON directory is missing.",
                    path=raw_dir,
                )
            )
            status = _merge_status(status, "error")
            continue

        json_files = sorted(path.rglob("*.json"))
        entry["json_files_count"] = len(json_files)

        if not json_files:
            entry["status"] = "warning"
            findings.append(
                _make_finding(
                    "warning",
                    "json_dir_empty",
                    "Allowed JSON directory has no JSON files.",
                    path=raw_dir,
                )
            )
            status = _merge_status(status, "warning")

        broken_files: list[str] = []
        for json_file in json_files:
            _, error = _load_json(json_file)
            if error:
                broken_files.append(str(json_file.relative_to(ROOT_DIR)).replace("\\", "/"))

        if broken_files:
            entry["status"] = "error"
            entry["broken_files"] = broken_files
            findings.append(
                _make_finding(
                    "error",
                    "json_decode_error",
                    "Directory contains unreadable JSON files.",
                    path=raw_dir,
                    broken_files=broken_files,
                )
            )
            status = _merge_status(status, "error")

        directories.append(entry)

    return {
        "status": status,
        "findings": findings,
        "details": {
            "directories": directories,
        },
    }


def probe_object_files() -> dict[str, Any]:
    status = "ok"
    findings: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []

    if not OBJECTS_DIR.exists() or not OBJECTS_DIR.is_dir():
        findings.append(
            _make_finding(
                "error",
                "objects_dir_missing",
                "Objects directory is missing.",
                path="app/data/objects",
            )
        )
        return {
            "status": "error",
            "findings": findings,
            "details": {
                "files": files,
            },
        }

    for object_file in sorted(OBJECTS_DIR.glob("*.json")):
        rel_path = str(object_file.relative_to(ROOT_DIR)).replace("\\", "/")
        entry: dict[str, Any] = {
            "path": rel_path,
            "status": "ok",
        }
        payload, error = _load_json(object_file)

        if error:
            entry["status"] = "error"
            entry["error"] = error
            files.append(entry)
            findings.append(
                _make_finding(
                    "error",
                    "object_json_unreadable",
                    "Object JSON file is unreadable.",
                    path=rel_path,
                    error=error,
                )
            )
            status = _merge_status(status, "error")
            continue

        if not isinstance(payload, dict):
            entry["status"] = "error"
            entry["error"] = "object root is not a JSON object"
            files.append(entry)
            findings.append(
                _make_finding(
                    "error",
                    "object_json_invalid_root",
                    "Object JSON root must be a JSON object.",
                    path=rel_path,
                )
            )
            status = _merge_status(status, "error")
            continue

        missing_fields = [field for field in REQUIRED_OBJECT_FIELDS if field not in payload]
        if missing_fields:
            entry["status"] = "error"
            entry["missing_fields"] = missing_fields
            findings.append(
                _make_finding(
                    "error",
                    "object_missing_fields",
                    "Object JSON is missing required fields.",
                    path=rel_path,
                    missing_fields=missing_fields,
                )
            )
            status = _merge_status(status, "error")

        languages = payload.get("languages")
        if "languages" in payload and not isinstance(languages, list):
            entry["status"] = "warning" if entry["status"] == "ok" else entry["status"]
            findings.append(
                _make_finding(
                    "warning",
                    "object_languages_type",
                    "Object field 'languages' is not a list.",
                    path=rel_path,
                )
            )
            status = _merge_status(status, "warning")

        is_partner = payload.get("is_partner")
        if "is_partner" in payload and not isinstance(is_partner, bool):
            entry["status"] = "warning" if entry["status"] == "ok" else entry["status"]
            findings.append(
                _make_finding(
                    "warning",
                    "object_is_partner_type",
                    "Object field 'is_partner' is not a boolean.",
                    path=rel_path,
                )
            )
            status = _merge_status(status, "warning")

        files.append(entry)

    if not files:
        findings.append(
            _make_finding(
                "warning",
                "objects_dir_empty",
                "Objects directory has no object JSON files.",
                path="app/data/objects",
            )
        )
        status = _merge_status(status, "warning")

    return {
        "status": status,
        "findings": findings,
        "details": {
            "files": files,
        },
    }

