from __future__ import annotations
from enum import Enum


class ErrorCode(str, Enum):
    FETCH_FAILED = "FETCH_FAILED"
    PARSE_FAILED = "PARSE_FAILED"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"


def health_ok(source_name: str, items_count: int, updated_at: str) -> dict:
    return {
        "source": source_name,
        "status": "ok",
        "items_count": items_count,
        "updated_at": updated_at,
        "error_code": None,
        "error_details": None,
    }


def health_expected_empty(source_name: str, updated_at: str) -> dict:
    return {
        "source": source_name,
        "status": "expected_empty",
        "items_count": 0,
        "updated_at": updated_at,
        "error_code": None,
        "error_details": None,
    }


def health_error(source_name: str, error_code: ErrorCode, error_details: str) -> dict:
    return {
        "source": source_name,
        "status": "error",
        "items_count": 0,
        "updated_at": None,
        "error_code": error_code,
        "error_details": error_details,
    }