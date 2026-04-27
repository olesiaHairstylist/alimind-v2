from playwright.sync_api import sync_playwright

URL = "https://kesinti.asat.gov.tr/dbo_kesintiListe/list"


def fetch_raw_data() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="tr-TR")
        page.goto(URL, wait_until="networkidle", timeout=30000)

        text = page.locator("body").inner_text()
        browser.close()

    if "Planlı Bir Kesinti bulunmamaktadır" in text:
        return []

    # дальше позже: парсинг строк таблицы, когда появятся реальные записи
    return []
def run_fetch() -> list[dict]:
    return fetch_raw_data()