from aiogram import Router, F
from aiogram.types import Message

from app.modules.group_moderation.rules import check_group_message
from app.modules.group_moderation.logger import log_moderation_action

router = Router(name="group_moderation_handlers")


RENT_SALE_TOPIC_IDS = {
    # сюда позже поставим ID тем "Аренда" и "Продажа"
    # пример:
    # 2,
    # 5,
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


def is_real_estate_topic(message: Message) -> bool:
    thread_id = getattr(message, "message_thread_id", None)

    if not RENT_SALE_TOPIC_IDS:
        return False

    return thread_id in RENT_SALE_TOPIC_IDS


def has_price(text: str) -> bool:
    lowered = text.lower()

    price_markers = ["€", "$", "₺", "tl", "try", "евро", "eur", "usd", "лир", "лира"]

    if any(marker in lowered for marker in price_markers):
        return True

    return False


def has_district(text: str) -> bool:
    lowered = text.lower()
    return any(district in lowered for district in DISTRICTS)


def has_contact(text: str) -> bool:
    lowered = text.lower()

    contact_markers = ["@", "whatsapp", "ватсап", "вацап", "тел", "phone", "+90", "+7"]

    return any(marker in lowered for marker in contact_markers)


def build_listing_hint(text: str) -> str | None:
    missing = []

    if not has_price(text):
        missing.append("— цену")

    if not has_district(text):
        missing.append("— район")

    if not has_contact(text):
        missing.append("— контакт")

    if not missing:
        return None

    return (
        "💡 Чтобы объявление лучше нашли, добавьте:\n"
        + "\n".join(missing)
    )


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def group_message_moderation(message: Message):

    text = message.text or message.caption or ""
    print("THREAD ID:", message.message_thread_id)
    print("CHAT:", message.chat.title)
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

    if not is_real_estate_topic(message):
        return

    hint = build_listing_hint(text)

    if not hint:
        return

    try:
        await message.reply(hint)

    except Exception as e:
        print(f"[GROUP SOFT STANDARDIZATION ERROR] {e}")