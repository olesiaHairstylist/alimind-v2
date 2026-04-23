import requests

URL = "https://alimindcity.com/wp-json/alimind/v1/partners"
TOKEN = "777777"

payload = {
    "id": "olesya_hairstylist",
    "title": "Olesya Hairstylist",
    "category": "beauty",
    "subcategory": "hair",
    "description_short": "Бьюти услуги в Алании",
    "description_full": "Стрижки любой сложности, современные техники окрашивания, восстановление и уход за волосами.",
    "location": "Alanya, Mahmutlar",
    "contact": "@olesya_hair_mahmutlar",
    "image_url": "https://alimindcity.com/wp-content/uploads/2026/04/photo_2026-01-16_13-31-12.jpg",
    "languages": ["ru"],
    "is_partner": True
}


headers = {
    "Content-Type": "application/json",
    "X-AliMind-Token": TOKEN,
}

response = requests.post(URL, json=payload, headers=headers, timeout=20)

print("STATUS:", response.status_code)
print("TEXT:", response.text)