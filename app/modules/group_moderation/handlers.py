import re
from aiogram import Router, F
from aiogram.types import Message
import requests
from app.modules.group_moderation.rules import check_group_message
from app.modules.group_moderation.logger import log_moderation_action
from aiogram.filters import Command
from app.modules.group_bridge.real_estate_to_group import publish_real_estate_to_group
router = Router(name="group_moderation_handlers")


# --- Topic IDs ---
# Топики где публикуют объявления: Аренда + Продажа
LISTING_TOPIC_IDS = {
    16,  # Аренда
    # добавить ID Продажа после debug
}

# Топик с запросами: Ищу квартиру
SEARCH_TOPIC_IDS = {
    # добавить ID Ищу квартиру после debug
}

DISTRICTS = [
    # RU

    "махмутлар",
    "оба",
    "оба гёль",
    "центр",
    "центр алании",
    "тосмур",
    "авсаллар",
    "конаклы",
    "газипаша",
    "кестель",
    "каргыджак",
    "джикджилли",
    "чикджилли",
    "демирташ",
    "окурджалар",
    "инжекум",
    "тюрклер",
    "пайяллар",
    "обагёль",
    "обагель",
    "чыплаклы",
    "алания",
    "алания центр",
    "центр аланья",
    "центральная алания",
    "район махмутлар",
    "район оба",
    "район авсаллар",
    "район кестель",
    "район каргыджак",
    "район тосмур",
    "район конаклы",
    "район джикджилли",
    "район чикджилли",
    "район газипаша",
    "район демирташ",
    "район тюрклер",
    "район пайяллар",
    "хаджет",
    "хаджет район",
    "район хаджет",

    # EN
    "mahmutlar",
    "oba",
    "obagol",
    "obagöl",
    "center",
    "alanya center",
    "central alanya",
    "tosmur",
    "avsallar",
    "konakli",
    "gazipasa",
    "gazipaşa",
    "kestel",
    "kargicak",
    "kargıcak",
    "cikcilli",
    "cıkcıllı",
    "ciplakli",
    "çıplaklı",
    "payallar",
    "turkler",
    "türkler",
    "demirtas",
    "demirtaş",
    "okurcalar",
    "incekum",
    "incekum",
    "alanya",
    "mahmutlar area",
    "oba area",
    "avsallar area",
    "kestel area",
    "tosmur area",
    "kargicak area",
    "konakli area",
    "hacet",
    "gazipasa area",
    "cikcilli area",
    "payallar area",
    "turkler area",
    "demirtas area",

    # TR
    "mahmutlar",
    "oba",
    "hacet area",
    "merkez",
    "tosmur",
    "avsallar",
    "konaklı",
    "gazipaşa",
    "kestel",
    "kargıcak",
    "cikcilli",
    "alanya",
    "obagöl",
    "obagol",
    "cıkgilli",
    "cikcilli",
    "çıplaklı",
    "ciplakli",
    "payallar",
    "demirtaş",
    "demirtas",
    "okurcalar",
    "inçekum",
    "incekum",
    "türkler",
    "turkler",
]


def get_topic_type(message: Message) -> str | None:
    """Возвращает тип топика: listing, search или None."""
    thread_id = getattr(message, "message_thread_id", None)

    if thread_id in LISTING_TOPIC_IDS:
        return "listing"

    if thread_id in SEARCH_TOPIC_IDS:
        return "search"

    return None


def has_price(text: str) -> bool:
    lowered = text.lower()

    # Валюты и слова
    price_markers = [
        "€", "$", "₺",
        "tl", "try",
        "eur", "usd",
        "euro",
        "евро",
        "лира", "лир",
        "доллар", "долл",
        "price",
        "цена",
        "стоимость",
    ]

    if any(marker in lowered for marker in price_markers):
        return True

    # Любые нормальные денежные суммы:
    # 79000
    # 79 000
    # 79.000
    # 79,000
    # 79k
    # 79 k
    # 1.250.000
    # 1 250 000

    money_patterns = [
        r"\b\d{2,3}[\s.,]?\d{3}\b",
        r"\b\d+\s?k\b",
        r"\b\d{1,3}(?:[\s.,]\d{3})+\b",
    ]

    return any(
        re.search(pattern, lowered)
        for pattern in money_patterns
    )


def has_district(text: str) -> bool:
    lowered = text.lower().replace("📍", " ")

    return any(
        district in lowered
        for district in DISTRICTS
    )


def has_contact(text: str) -> bool:
    lowered = text.lower()
    contact_markers = ["@", "whatsapp", "ватсап", "вацап", "тел", "phone", "+90", "+7"]
    return any(marker in lowered for marker in contact_markers)

def build_listing_hint(text: str) -> str | None:
    """Подсказка для топиков Аренда / Продажа."""
    missing = []

    if not has_price(text):
        missing.append("— цену")

    if not has_district(text):
        missing.append("— район")

    # ВРЕМЕННО отключено, чтобы бот меньше раздражал людей
    # if not has_contact(text):
    #     missing.append("— контакт")

    if not missing:
        return None

    return "💡 Чтобы объявление лучше нашли, добавьте:\n" + "\n".join(missing)


def build_search_hint(text: str) -> str | None:
    """Подсказка для топика Ищу квартиру."""
    missing = []

    if not has_district(text):
        missing.append("— район")

    if not has_price(text):
        missing.append("— бюджет, если готовы указать")

    # ВРЕМЕННО отключено, чтобы бот меньше раздражал людей
    # if not has_contact(text):
    #     missing.append("— контакт")

    if not missing:
        return None

    return "💡 Чтобы владельцы могли вам написать, добавьте:\n" + "\n".join(missing)
@router.message(Command("post_real_estate"))
async def post_real_estate(message: Message):

    result = await publish_real_estate_to_group(message.bot)

    if result:
        await message.answer("✅ Объекты отправлены в группу")
    else:
        await message.answer("📭 Новых объектов для публикации нет")
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_moderation(message: Message):
    text = message.text or message.caption or ""

    # Если это фото/медиа без текста — не трогаем
    if not text.strip():
        return

    # TEMP DEBUG: собрать карту топиков
    thread_id = getattr(message, "message_thread_id", None)
    print(f"[DEBUG GROUP] thread_id={thread_id} | text={text[:60]}")
    print("SITE POST START")

    response = requests.post(
        "https://alimindcity.com/wp-json/alimind/v1/group-test",
        json={
            "chat_id": message.chat.id,
            "thread_id": thread_id,
            "text": text,
        },
        timeout=10,
    )

    print(
        "SITE RESPONSE:",
        response.status_code,
        response.text
    )
    # --- Спам / мусор — удаляем ---
    result = check_group_message(text)

    if result["delete"]:
        try:
            await message.delete()
            await log_moderation_action(
                message=message,
                reason=result["reason"],
            )
        except Exception as e:
            print(f"[GROUP MODERATION ERROR] {e}")
        return

    # --- Мягкая стандартизация только в нужных топиках ---
    topic_type = get_topic_type(message)

    if topic_type == "listing":
        hint = build_listing_hint(text)
    elif topic_type == "search":
        hint = build_search_hint(text)
    else:
        return

    if not hint:
        return

    try:
        await message.reply(hint)
    except Exception as e:
        print(f"[GROUP SOFT STANDARDIZATION ERROR] {e}")