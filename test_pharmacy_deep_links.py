from app.handlers.start import _extract_start_pharmacy_code
from app.modules.city_events.services.pharmacy_districts import (
    district_label,
    filter_pharmacies,
    item_district_code,
)


class FakeMessage:
    def __init__(self, text: str):
        self.text = text


ITEMS = [
    {
        "title": "EMİR ECZANESİ",
        "details": "Дежурная аптека (MAHMUTLAR)",
        "address": "ATATÜRK CAD. NO:129/A",
        "phone": "0(242) 528-71-73",
    },
    {
        "title": "OBA ECZANESİ",
        "details": "Дежурная аптека (OBA)",
        "address": "OBA MAH. ALANYA",
        "phone": "0(242) 000-00-00",
    },
]


def test_extracts_supported_deep_link_payload():
    assert _extract_start_pharmacy_code(FakeMessage("/start pharmacy_mahmutlar")) == "mahmutlar"
    assert _extract_start_pharmacy_code(FakeMessage("/start pharmacy_all")) == "all"


def test_plain_start_is_unchanged():
    assert _extract_start_pharmacy_code(FakeMessage("/start")) is None
    assert _extract_start_pharmacy_code(FakeMessage("/start obj_example")) is None


def test_filters_by_authoritative_source_region():
    assert item_district_code(ITEMS[0]) == "mahmutlar"
    assert filter_pharmacies(ITEMS, "mahmutlar") == [ITEMS[0]]
    assert filter_pharmacies(ITEMS, "oba") == [ITEMS[1]]


def test_all_returns_full_list_and_unknown_is_safe():
    assert filter_pharmacies(ITEMS, "all") == ITEMS
    assert filter_pharmacies(ITEMS, "unknown") == []
    assert district_label("unknown") is None


def test_turkish_district_names_are_normalized():
    item = {"details": "Nöbetçi eczane (ÇIKÇILLI)", "address": ""}
    assert item_district_code(item) == "cikcilli"
