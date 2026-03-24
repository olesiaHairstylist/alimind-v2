import requests

BASE = "https://www.alanyaeo.org.tr"
URL = f"{BASE}/tr/eczane/getir"

headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE}/tr/nobetci-eczaneler",
    "User-Agent": "Mozilla/5.0",
}

for bolge_id in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
    try:
        r = requests.post(URL, data={"bolgeId": bolge_id}, headers=headers, timeout=20)
        print("=" * 60)
        print("BOLGE:", bolge_id)
        print("STATUS:", r.status_code)
        print("CONTENT-TYPE:", r.headers.get("Content-Type"))
        print("TEXT:", r.text[:1000])
    except Exception as e:
        print("BOLGE:", bolge_id, "ERROR:", e)