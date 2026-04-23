from enum import Enum
from typing import TypedDict, Optional


class SourceStatus(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
    EMPTY = "empty"


class SourceHealthEntry(TypedDict):
    source: str
    status: str
    last_success_at: Optional[str]
    last_check_at: Optional[str]
    consecutive_failures: int
    error: Optional[str]
    items_count: Optional[int]