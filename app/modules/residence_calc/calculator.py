from __future__ import annotations

from app.modules.residence_calc.data import CARD_FEE_TL, COUNTRIES


def calculate_residence_fee(country_code: str, months: int, is_first_application: bool) -> dict:
    if country_code not in COUNTRIES:
        raise ValueError("Unknown country code")

    if months < 1:
        raise ValueError("Months must be 1 or more")

    country = COUNTRIES[country_code]

    first_month = country["first_month_usd"]
    next_month = country["next_month_usd"]

    fee_usd = first_month + (months - 1) * next_month

    tek_giris_applies = bool(
        is_first_application and country["tek_giris_required"]
    )

    return {
        "country_name": country["name"],
        "months": months,
        "is_first_application": is_first_application,
        "first_month_usd": first_month,
        "next_month_usd": next_month,
        "fee_usd": round(fee_usd, 2),
        "card_fee_tl": CARD_FEE_TL,
        "tek_giris_applies": tek_giris_applies,
    }