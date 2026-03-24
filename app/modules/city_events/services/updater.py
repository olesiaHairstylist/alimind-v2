from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.modules.city_events.contracts.categories import CityEventCategory
from app.modules.city_events.sources.pharmacies_html_source import fetch_pharmacies_from_html
from app.modules.city_events.storage.schema import CityEventItem, CityEventPayload
from app.modules.city_events.storage.writer import write_payload


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "city_events"


def update_emergency_contacts() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    items = [
        CityEventItem(
            title="112 Acil Çağrı Merkezi",
            details="Единый экстренный номер",
            phone="112",
        ),
        CityEventItem(
            title="Пожарная служба",
            details="Пожарная помощь",
            phone="110",
        ),
        CityEventItem(
            title="Полиция",
            details="Полиция / экстренный вызов",
            phone="155",
        ),
    ]

    payload = CityEventPayload(
        category=CityEventCategory.EMERGENCY,
        updated_at=now,
        items=items,
    )

    write_payload(DATA_DIR, payload)


def update_pharmacies() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    raw_items = fetch_pharmacies_from_html()

    items: list[CityEventItem] = []

    for raw in raw_items:
        name = str(raw.get("name", "")).strip()
        details = str(raw.get("details", "")).strip()
        address = str(raw.get("address", "")).strip()
        phone = str(raw.get("phone", "")).strip()

        if not name:
            continue

        items.append(
            CityEventItem(
                title=name,
                details=details,
                address=address,
                phone=phone,
            )
        )

    payload = CityEventPayload(
        category=CityEventCategory.PHARMACIES,
        updated_at=now,
        items=items,
    )

    written = write_payload(DATA_DIR, payload)
    print("WRITTEN:", written.resolve())
    print("UPDATED_AT:", now)
    print("ITEMS COUNT:", len(items))


if __name__ == "__main__":
    update_pharmacies()
    print("CWD:", Path.cwd())
    print("DATA_DIR:", DATA_DIR.resolve())