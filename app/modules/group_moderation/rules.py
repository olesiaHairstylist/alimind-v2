SPAM_WORDS = [
    "казино",
    "casino",
    "ставки",
    "bet",
    "заработок",
    "доход",
    "инвестиции",
    "crypto",
    "крипта",
    "escort",
    "18+",
]


def check_group_message(text: str) -> dict:

    text_lower = text.lower()

    for word in SPAM_WORDS:

        if word in text_lower:
            return {
                "delete": True,
                "reason": f"spam_word:{word}",
            }

    if "t.me/" in text_lower or "telegram.me/" in text_lower:
        return {
            "delete": True,
            "reason": "external_telegram_link",
        }

    return {
        "delete": False,
        "reason": None,
    }