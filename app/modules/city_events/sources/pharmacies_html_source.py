import re
import requests
from bs4 import BeautifulSoup


URL = "https://www.alanyaeo.org.tr/tr/nobetci-eczaneler"

PHONE_RE = re.compile(r"0\(\d{3}\)\s*\d{3}-\d{2}-\d{2}")


def _clean(text: str) -> str:
    return " ".join(text.split()).strip()


def fetch_pharmacies_from_html() -> list[dict]:
    resp = requests.get(URL, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Берём основной текстовый поток страницы
    lines: list[str] = []
    for s in soup.stripped_strings:
        text = _clean(str(s))
        if text:
            lines.append(text)

    items: list[dict] = []

    # Ищем начало нужного блока
    try:
        start = lines.index("Nöbetçi Eczane Listesi") + 1
    except ValueError:
        return items

    current_region = ""
    i = start

    while i < len(lines):
        line = lines[i]

        # стоп на следующем большом блоке страницы
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

        # район: обычно UPPERCASE и не телефон
        if (
            line == line.upper()
            and not PHONE_RE.fullmatch(line)
            and "ECZANESİ" not in line
            and len(line) > 2
        ):
            current_region = line
            i += 1
            continue

        # запись аптеки: название + следующий телефон + потом адрес
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