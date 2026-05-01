from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.modules.core.language.service import get_user_lang
from app.modules.sea_status.sea_status import get_sea_status
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()

def build_sea_back_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Назад в меню", callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()

@router.callback_query(F.data == "sea_status:open")
async def sea_status_handler(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id) or "ru"
    data = get_sea_status()

    if not data["ok"]:
        msg = {
            "ru": "⚠️ Не удалось получить данные о море. Попробуйте позже.",
            "en": "⚠️ Failed to get sea data. Please try again later.",
            "tr": "⚠️ Deniz verileri alınamadı. Lütfen tekrar deneyin.",
        }.get(lang, "⚠️ Не удалось получить данные о море.")
        await callback.message.answer(msg)
        await callback.answer()
        return

    wind_str = {
        "ru": f"{data['wind']} м/с" if data["wind"] is not None else "нет данных",
        "en": f"{data['wind']} m/s" if data["wind"] is not None else "no data",
        "tr": f"{data['wind']} m/s" if data["wind"] is not None else "veri yok",
    }.get(lang, f"{data['wind']} м/с")

    titles = {
        "ru": "🌊 Море в Алании сейчас",
        "en": "🌊 Sea in Alanya now",
        "tr": "🌊 Alanya'da deniz şimdi",
    }
    labels = {
        "ru": ("🌡 Температура воды", "🌊 Волны", "💨 Ветер", "🕐 Обновлено"),
        "en": ("🌡 Water temperature", "🌊 Waves", "💨 Wind", "🕐 Updated"),
        "tr": ("🌡 Su sıcaklığı", "🌊 Dalgalar", "💨 Rüzgar", "🕐 Güncellendi"),
    }.get(lang, ("🌡 Температура воды", "🌊 Волны", "💨 Ветер", "🕐 Обновлено"))

    text = (
        f"{titles.get(lang, titles['ru'])}\n\n"
        f"{labels[0]}: {data['temp']}°C\n"
        f"{labels[1]}: {data['waves']} м\n"
        f"{labels[2]}: {wind_str}\n\n"
        f"{data['verdict']}\n\n"
        f"{labels[3]}: {data['updated']}"
    )
    texts = {
        "ru": {
            "verdict": {
                "excellent": "🟢 Отлично — идти купаться",
                "normal": "🟡 Норм — но волны есть",
                "bad": "🔴 Не лучший день для пляжа",
            }
        },
        "en": {
            "verdict": {
                "excellent": "🟢 Great — perfect for swimming",
                "normal": "🟡 Okay — some waves",
                "bad": "🔴 Not the best day for the beach",
            }
        },
        "tr": {
            "verdict": {
                "excellent": "🟢 Harika — yüzmek için uygun",
                "normal": "🟡 Fena değil — dalga var",
                "bad": "🔴 Deniz için uygun değil",
            }
        },
    }

    # получаем текст verdict с переводом и эмодзи
    verdict_text = texts.get(lang, texts["ru"])["verdict"].get(
        data["verdict"], data["verdict"]
    )

    text = (
        f"{titles.get(lang, titles['ru'])}\n\n"
        f"{labels[0]}: {data['temp']}°C\n"
        f"{labels[1]}: {data['waves']} м\n"
        f"{labels[2]}: {wind_str}\n\n"
        f"{verdict_text}\n\n"
        f"{labels[3]}: {data['updated']}"
    )
    await callback.message.answer(
        text,
        reply_markup=build_sea_back_kb(),
    )
    await callback.answer()