from aiogram import Router, F
from aiogram.types import Message

from app.modules.group_moderation.rules import check_group_message
from app.modules.group_moderation.logger import log_moderation_action

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
    "махмутлар",
    "оба",
    "центр",
    "тосмур",
    "авсаллар",
    "конаклы",
    "газипаша",
    "кестель",
    "каргыджак",
    "джикджилли",
    "чикджилли",
    "алания",
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
    price_markers = ["€", "$", "₺", "tl", "try", "евро", "eur", "usd", "лир", "лира"]
    return any(marker in lowered for marker in price_markers)


def has_district(text: str) -> bool:
    lowered = text.lower()
    return any(district in lowered for district in DISTRICTS)


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

    if not has_contact(text):
        missing.append("— контакт")

    if not missing:
        return None

    return "💡 Чтобы объявление лучше нашли, добавьте:\n" + "\n".join(missing)


def build_search_hint(text: str) -> str | None:
    """Подсказка для топика Ищу квартиру."""
    missing = []

    if not has_district(text):
        missing.append("— район")

    if not has_contact(text):
        missing.append("— контакт")

    if not has_price(text):
        missing.append("— бюджет, если готовы указать")

    if not missing:
        return None

    return "💡 Чтобы владельцы могли вам написать, добавьте:\n" + "\n".join(missing)


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_moderation(message: Message):
    text = message.text or message.caption or ""

    # TEMP DEBUG: собрать карту топиков
    thread_id = getattr(message, "message_thread_id", None)
    print(f"[DEBUG GROUP] thread_id={thread_id} | text={text[:60]}")

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