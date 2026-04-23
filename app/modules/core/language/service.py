from __future__ import annotations

import json
from pathlib import Path

LANG_STORAGE_PATH = Path("app/data/system/user_languages.json")
SUPPORTED_LANGS = {"ru", "en", "tr"}


def _load_all() -> dict[str, str]:
    if not LANG_STORAGE_PATH.exists():
        return {}

    try:
        data = json.loads(LANG_STORAGE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    result: dict[str, str] = {}
    for user_id, lang in data.items():
        if isinstance(user_id, str) and isinstance(lang, str) and lang in SUPPORTED_LANGS:
            result[user_id] = lang

    return result


def _save_all(data: dict[str, str]) -> None:
    LANG_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LANG_STORAGE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_user_lang(user_id: int) -> str | None:
    return _load_all().get(str(user_id))


def set_user_lang(user_id: int, lang: str) -> None:
    if lang not in SUPPORTED_LANGS:
        return

    data = _load_all()
    data[str(user_id)] = lang
    _save_all(data)
