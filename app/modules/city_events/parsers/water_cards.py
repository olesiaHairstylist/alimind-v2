from __future__ import annotations

from app.modules.city_events.storage.schema import CityEventItem


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split()).strip()


def parse_water_items_from_html(html: str) -> list[CityEventItem]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    if "Planlı Bir Kesinti bulunmamaktadır" in text:
        return []

    items: list[CityEventItem] = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [clean_text(td.get_text(" ", strip=True)) for td in row.find_all("td")]

            if len(cols) < 4:
                continue

            district = cols[0]
            neighborhood = cols[1] if len(cols) > 1 else ""
            start_at = cols[2] if len(cols) > 2 else ""
            end_at = cols[3] if len(cols) > 3 else ""
            reason = cols[4] if len(cols) > 4 else ""
            affected = cols[5] if len(cols) > 5 else ""
            street = cols[6] if len(cols) > 6 else ""

            if district and "ALANYA" not in district.upper():
                continue

            details_parts: list[str] = []

            if reason:
                details_parts.append(f"Причина: {reason}")
            if start_at:
                details_parts.append(f"Начало: {start_at}")
            if end_at:
                details_parts.append(f"Окончание: {end_at}")
            if affected:
                details_parts.append(f"Затронуто: {affected}")

            items.append(
                CityEventItem(
                    title=neighborhood or district or "Отключение воды",
                    details="\n".join(details_parts),
                    address=street,
                    phone="",
                )
            )

    return items