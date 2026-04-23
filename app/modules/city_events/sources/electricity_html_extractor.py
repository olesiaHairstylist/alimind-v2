from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

SPACE_RE = re.compile(r"\s+")
ENTRY_START_RE = re.compile(r"(?=\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s*-\s*\d{2}:\d{2})")
DATETIME_RANGE_RE = re.compile(
    r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\s*-\s*"
    r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})"
)
NOTE_RE = re.compile(r"Kesinti Nedeni:\s*(.+?)(?=\s+Etkilenen Cadde\s*/\s*Sokak|\s*$)", re.IGNORECASE)
STREETS_RE = re.compile(
    r"Etkilenen Cadde\s*/\s*Sokak\s+(.+?)(?=\s+bölgelerinde\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s*-\s*\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}|\s*$)",
    re.IGNORECASE,
)
TAIL_RANGE_RE = re.compile(
    r"bölgelerinde\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\s*-\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
    re.IGNORECASE,
)

PAGE_GARBAGE_MARKERS = (
    "Ana Sayfa",
    "Kurumsal AEDAŞ",
    "Bilgi Toplumu Hizmetleri",
    "Yeni Abonelik",
    "Kesinti Haritası",
    "PLANLI ELEKTRİK KESİNTİLERİ",
    "Şirketimiz Elder Üyesidir",
    "Tüm Hakları Saklıdır",
)


def _clean(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def _normalize_note(note: str) -> str:
    note = _clean(note)
    replacements = {
        "Çalışması": "Çalışması",
        "Calismasi": "Çalışması",
        "Çalişmasi": "Çalışması",
        "Çalışmasi": "Çalışması",
        "Calışması": "Çalışması",
        "Manevra Çalışması": "Manevra Çalışması",
        "Bakım Çalışması": "Bakım Çalışması",
        "Yatırım Çalışması": "Yatırım Çalışması",
    }

    for old, new in replacements.items():
        note = note.replace(old, new)

    return note


def _strip_page_garbage(text: str) -> str:
    text = _clean(text)

    for marker in PAGE_GARBAGE_MARKERS:
        pos = text.find(marker)
        if pos > 0:
            text = text[:pos].strip()

    return text


def _split_entries(full_text: str) -> list[str]:
    """
    Режет страницу на записи по старту вида:
    26.02.2026 09:30 - 16:30
    """
    chunks = ENTRY_START_RE.split(full_text)
    result: list[str] = []

    for chunk in chunks:
        chunk = _clean(chunk)
        if not chunk:
            continue
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s*-\s*\d{2}:\d{2}", chunk):
            continue
        result.append(chunk)

    return result


def _extract_note(text: str) -> str:
    match = NOTE_RE.search(text)
    if not match:
        return ""

    return _normalize_note(match.group(1))


def _extract_datetime_range(text: str) -> tuple[str, str]:
    """
    Берём точный диапазон с секундами из хвоста записи:
    26/02/2026 09:30:00 - 26/02/2026 16:30:00
    """
    match = TAIL_RANGE_RE.search(text)
    if match:
        return _clean(match.group(1)), _clean(match.group(2))

    match = DATETIME_RANGE_RE.search(text)
    if match:
        return _clean(match.group(1)), _clean(match.group(2))

    return "", ""


def _extract_streets_blob(text: str) -> str:
    match = STREETS_RE.search(text)
    if not match:
        return ""

    return _clean(match.group(1))


def _extract_title(streets_blob: str) -> str:
    """
    Title = компактная строка affected streets только по ALANYA.
    """
    if not streets_blob:
        return ""

    upper = streets_blob.upper()
    start = upper.find("ANTALYA,ALANYA")
    if start == -1:
        return ""

    snippet = streets_blob[start:]
    snippet = re.split(r";\s*[A-ZÇĞİÖŞÜ]+\s*,\s*[A-ZÇĞİÖŞÜ]+", snippet, maxsplit=1)[0]
    snippet = _clean(snippet)

    return snippet[:300].rstrip(" ,;")


def _extract_clean_details(text: str) -> str:
    """
    Оставляем только полезную часть записи:
    дата + причина + affected streets + точный диапазон.
    """
    text = _strip_page_garbage(text)

    # Обрезаем всё после первой следующей записи, если вдруг прилипло
    next_entry = re.search(r"\s\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s*-\s*\d{2}:\d{2}", text[1:])
    if next_entry:
        text = text[: next_entry.start() + 1].strip()

    return text[:1200].strip()


def extract_outage_blocks_from_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    full_text = _clean(soup.get_text(" ", strip=True))

    entries = _split_entries(full_text)
    items: list[dict[str, Any]] = []

    for entry in entries:
        upper_entry = entry.upper()

        if "ALANYA" not in upper_entry:
            continue

        streets_blob = _extract_streets_blob(entry)
        title = _extract_title(streets_blob)
        start_at, end_at = _extract_datetime_range(entry)
        note = _extract_note(entry)
        details = _extract_clean_details(entry)

        if not title and streets_blob:
            title = streets_blob[:300].rstrip(" ,;")

        if not any([title, start_at, end_at, note, details]):
            continue

        items.append(
            {
                "title": title,
                "start_at": start_at,
                "end_at": end_at,
                "note": note,
                "details": details,
                "address": "",
                "phone": "",
            }
        )

    return _dedup_items(items)


def filter_alanya_blocks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Оставляем для совместимости вызовов.
    После нового extractor записи уже должны быть только по ALANYA,
    но фильтр сохраняем как дополнительную страховку.
    """
    result: list[dict[str, Any]] = []

    for item in items:
        blob = " ".join(
            str(item.get(field, "")) for field in ("title", "details", "note")
        ).upper()

        if "ALANYA" not in blob:
            continue

        result.append(item)

    return _dedup_items(result)


def _dedup_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for item in items:
        key = (
            _clean(str(item.get("title", ""))).upper(),
            _clean(str(item.get("start_at", ""))),
            _clean(str(item.get("end_at", ""))),
            _clean(str(item.get("note", ""))).upper(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique