from __future__ import annotations


def render_residence_fee_result(result: dict) -> str:
    app_type = "первичная подача" if result["is_first_application"] else "продление"

    tek_giris_text = (
        "применяется, сумму нужно уточнить отдельно"
        if result["tek_giris_applies"]
        else "не применяется"
    )

    return (
        "🧾 <b>Расчёт сборов ВНЖ</b>\n\n"

        f"🌍 <b>Гражданство:</b> {result['country_name']}\n"
        f"📅 <b>Срок:</b> {result['months']} мес.\n"
        f"📌 <b>Тип подачи:</b> {app_type}\n\n"

        "💰 <b>Госпошлина:</b>\n"
        f"{result['first_month_usd']}$ + "
        f"{result['months'] - 1} × {result['next_month_usd']}$ "
        f"= <b>{result['fee_usd']}$</b>\n\n"

        "🪪 <b>Карточка ВНЖ:</b>\n"
        f"{result['card_fee_tl']} TL\n\n"

        "🚪 <b>Дополнительный сбор Tek Giriş:</b>\n"
        f"{tek_giris_text}\n\n"

        "📊 <b>Итого:</b>\n"
        f"<b>{result['fee_usd']}$ + {result['card_fee_tl']} TL</b>\n\n"

        "⚠️ <i>Расчёт ориентировочный. Перед подачей проверяйте актуальные суммы на официальном источнике.</i>"
    )
