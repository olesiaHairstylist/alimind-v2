import requests
from aiogram import Bot

GROUP_ID = -1003850900971

SOURCE_URL = "https://alimindcity.com/wp-json/alimind/v1/real-estate-for-group"

MARK_URL = "https://alimindcity.com/wp-json/alimind/v1/mark-group-posted"


async def publish_real_estate_to_group(bot: Bot):

    response = requests.get(SOURCE_URL, timeout=10)

    data = response.json()

    objects = data.get("objects", [])

    if not objects:
        return False

    for obj in objects:

        text = format_real_estate_post(obj)

        photos = obj.get("photos") or []

        if photos:
            await bot.send_photo(
                chat_id=GROUP_ID,
                photo=photos[0],
                caption=text,
            )

        else:
            await bot.send_message(
                chat_id=GROUP_ID,
                text=text,
            )

        mark_response = requests.post(
            MARK_URL,
            json={
                "id": obj.get("id")
            },
            timeout=10,
        )

        print(
            "MARK POSTED:",
            mark_response.status_code,
            mark_response.text
        )

    return True


def format_real_estate_post(obj: dict) -> str:

    deal_type = (
        "Продажа"
        if obj.get("type") == "sale"
        else "Аренда"
    )

    return f"""🏡 {deal_type} недвижимости в Алании

📍 Район: {obj.get("district", "")}
🏠 Комнат: {obj.get("rooms", "")}
💰 Цена: {obj.get("price", "")} {obj.get("currency", "")}

{obj.get("description", "")}

📩 Telegram: {obj.get("telegram", "")}
📞 WhatsApp: {obj.get("whatsapp", "")}

Источник: AliMind City
"""