from app.handlers.start import _extract_start_pharmacy_code
from app.modules.city_events.services.pharmacy_districts import (
    district_label,
    filter_pharmacies,
    item_district_code,
)
from app.modules.city_events.ui.handlers import (
    _pharmacy_card_kb,
    _pharmacy_card_text,
    build_pharmacy_districts_kb,
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


def test_precise_address_district_wins_over_broad_source_region():
    item = {
        "details": "Дежурная аптека (ALANYA MERKEZ)",
        "address": "OBA MAH. ALANYA EĞİTİM ARAŞTIRMA HASTANESİ",
    }
    assert item_district_code(item) == "oba"


def test_route_uses_proven_google_maps_search_format():
    markup = _pharmacy_card_kb(ITEMS[0], "Mahmutlar", "ru")
    url = markup.inline_keyboard[0][0].url
    assert url is not None
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "EM%C4%B0R+ECZANES%C4%B0" in url
    assert "ATAT" in url


def test_card_does_not_create_fake_cad_no_link():
    text = _pharmacy_card_text(ITEMS[0], "Mahmutlar", "ru")
    assert "CAD.NO:" not in text
    assert "CAD. NO 129/A" in text


def test_full_list_navigation_leads_to_main_menu_not_full_list_again():
    markup = build_pharmacy_districts_kb("ru", show_all=False)
    callbacks = [
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data
    ]
    assert "main:menu" in callbacks
    assert "pharmacy:district:all" not in callbacks


def test_district_navigation_offers_full_list_and_main_menu():
    markup = build_pharmacy_districts_kb("ru", show_all=True)
    callbacks = [
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data
    ]
    assert "pharmacy:district:all" in callbacks
    assert "main:menu" in callbacks


def test_pharmacy_navigation_offers_return_to_website():
    markup = build_pharmacy_districts_kb("ru")
    urls = [
        button.url
        for row in markup.inline_keyboard
        for button in row
        if button.url
    ]
    assert "https://alimindcity.com/" in urls


def test_route_prefers_exact_pharmacy_name_over_approximate_coordinates():
    item = dict(ITEMS[0])
    item["maps_url"] = (
        "https://www.google.com/maps/dir/?api=1&destination="
        "36.48386893014357,32.1057536388447"
    )
    markup = _pharmacy_card_kb(item, "Mahmutlar", "ru")
    url = markup.inline_keyboard[0][0].url
    assert url is not None
    assert "destination=EM%C4%B0R+ECZANES%C4%B0%2C+Mahmutlar%2C+Alanya" in url
    assert "36.483868" not in url
