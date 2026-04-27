from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from app.data.system.source_health_contracts import (
    health_ok,
    health_error,
    ErrorCode,
)
from app.data.system.health_writer import write_health


APP_DIR = Path(__file__).resolve().parents[3]
RAW_FILE = APP_DIR / "data" / "sources" / "pharmacies_raw.json"

URL = "https://www.alanyaeo.org.tr/tr/nobetci-eczaneler"
PHONE_RE = re.compile(r"0\(\d{3}\)\s*\d{3}-\d{2}-\d{2}")

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")


def now_tr_iso() -> str:
    return datetime.now(ISTANBUL_TZ).isoformat()


def _clean(text: str) -> str:
    return " ".join(text.split()).strip()


def fetch_pharmacies_from_html() -> list[dict]:
    resp = requests.get(URL, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    lines: list[str] = []
    for s in soup.stripped_strings:
        text = _clean(str(s))
        if text:
            lines.append(text)

    items: list[dict] = []

    try:
        start = lines.index("Nöbetçi Eczane Listesi") + 1
    except ValueError:
        return items

    current_region = ""
    i = start

    while i < len(lines):
        line = lines[i]

        if line in {
            "Türk Eczacıları Birliği",
            "Eczacı Odaları",
            "Ecza Depoları",
            "Antalya İl Sağlık Müdürlüğü",
            "Aile Hekimi Sorgulama",
            "SGK ve Kurumlar",
            "TBMM Reçete Giriş",
            "T.C. Kimlik No Sorgulama",
            "SSK E-Borcu Yoktur",
            "SGK Bilgi Edinme",
            "Risk Analiz Formu",
            "SGK Denetimleri",
            "Görüş ve Öneriler",
            "Bize Ulaşın",
        }:
            break

        if (
            line == line.upper()
            and not PHONE_RE.fullmatch(line)
            and "ECZANESİ" not in line
            and len(line) > 2
        ):
            current_region = line
            i += 1
            continue

        if "ECZANESİ" in line:
            name = line
            phone = ""
            address = ""

            if i + 1 < len(lines) and PHONE_RE.fullmatch(lines[i + 1]):
                phone = lines[i + 1]

            if i + 2 < len(lines):
                address = lines[i + 2]

            items.append(
                {
                    "name": name,
                    "details": f"Дежурная аптека ({current_region})" if current_region else "Дежурная аптека",
                    "address": address,
                    "phone": phone,
                }
            )

            i += 3
            continue

        i += 1

    return items


def save_raw(data: list[dict]) -> Path:
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return RAW_FILE


def write_pharmacies_health(items: list[dict]) -> None:
    if not items:
        write_health(
            health_error(
                source_name="pharmacies",
                error_code=ErrorCode.INVALID_PAYLOAD,
                error_details="No pharmacy items parsed from HTML source",
            )
        )
        return

    write_health(
        health_ok(
            source_name="pharmacies",
            items_count=len(items),
            updated_at=now_tr_iso(),
        )
    )


def write_pharmacies_health_error(error: Exception) -> None:
    error_code = ErrorCode.TIMEOUT if isinstance(error, requests.Timeout) else ErrorCode.FETCH_FAILED

    write_health(
        health_error(
            source_name="pharmacies",
            error_code=error_code,
            error_details=str(error),
        )
    )


def run_fetch() -> Path:
    try:
        data = fetch_pharmacies_from_html()
        print("FETCHED:", len(data))

        path = save_raw(data)
        write_pharmacies_health(data)

        return path

    except Exception as e:
        write_pharmacies_health_error(e)
        print("FETCH ERROR:", e)
        raise


if __name__ == "__main__":
    path = run_fetch()
    print("RAW SAVED:", path)
    print("ABS:", path.resolve())