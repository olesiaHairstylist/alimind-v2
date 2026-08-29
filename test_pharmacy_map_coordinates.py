from bs4 import BeautifulSoup

from app.modules.city_events.sources.pharmacies_source import _map_urls_by_address


def test_extracts_official_map_coordinates_by_address():
    soup = BeautifulSoup(
        """
        <a href="https://maps.google.com/maps?q=36.541561927647834,32.04257011413574&amp;hl=es;z=16&amp;output=embed">
          OBA MAH. ALANYA EĞİTİM ARAŞTIRMA HASTANESİ
        </a>
        """,
        "html.parser",
    )
    result = _map_urls_by_address(soup)
    assert result == {
        "OBA MAH. ALANYA EĞİTİM ARAŞTIRMA HASTANESİ": (
            "https://www.google.com/maps/dir/?api=1&destination="
            "36.541561927647834,32.04257011413574"
        )
    }
