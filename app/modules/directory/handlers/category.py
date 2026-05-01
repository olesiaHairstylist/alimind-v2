from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.modules.core.language.service import get_user_lang
from app.modules.directory.contracts.callbacks import (
    is_directory_category_cb,
    parse_directory_category_cb,
)
from app.modules.directory.contracts.categories import get_category_title
from app.modules.directory.render.keyboard_render import build_directory_subcategories_kb
from app.modules.directory.services.loader import load_subcategories
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()
STUB_CATEGORY_IDS = {"health", "home", "kids"}
def build_about_text(lang: str = "ru") -> str:
    return {
        "ru": (
            "ℹ️ AliMind — городской помощник в Алании\n\n"
            "Бот помогает быстро найти:\n"
            "• услуги и мастеров\n"
            "• актуальную информацию по городу\n"
            "• полезные инструменты\n\n"
            "📬 Связь:\n"
            "@Alimind_07\n\n"
            "🌐 Сайт:\n"
            "https://alimindcity.com/"
        ),
        "en": "AliMind — city assistant",
        "tr": "AliMind — şehir asistanı",
    }.get(lang, "")


def build_about_kb():
    b = InlineKeyboardBuilder()
    b.button(text="📨 Связаться", url="https://t.me/Ali_sur")
    b.button(text="🌐 Сайт", url="https://alimindcity.com/")
    b.button(text="⬅️ Назад", callback_data="directory:menu")
    b.adjust(1)
    return b.as_markup()

def build_category_stub_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Назад к категориям", callback_data="directory:menu")
    b.button(text="🏠 Главное меню", callback_data="main:menu")
    b.adjust(1)
    return b.as_markup()


def _stub_text(category_title: str, lang: str) -> str:
    return {
        "ru": f"🚧 {category_title}\n\nРаздел скоро будет работать.",
        "en": f"🚧 {category_title}\n\nThis section will be available soon.",
        "tr": f"🚧 {category_title}\n\nBu bölüm yakında çalışacak.",
    }.get(lang, f"🚧 {category_title}\n\nРаздел скоро будет работать.")

def _texts(lang: str) -> dict[str, str]:
    return {
        "ru": {
            "error": "Ошибка категории",
            "empty": "Подкатегории не найдены",
            "choose": "Выберите подкатегорию:",
        },
        "en": {
            "error": "Category error",
            "empty": "No subcategories found",
            "choose": "Choose a subcategory:",
        },
        "tr": {
            "error": "Kategori hatası",
            "empty": "Alt kategoriler bulunamadı",
            "choose": "Bir alt kategori seçin:",
        },
    }.get(lang, {
        "error": "Ошибка категории",
        "empty": "Подкатегории не найдены",
        "choose": "Выберите подкатегорию:",
    })


@router.callback_query(F.data.func(is_directory_category_cb))
async def open_directory_category(callback: CallbackQuery) -> None:
    data = callback.data or ""
    category_id = parse_directory_category_cb(data)
    lang = get_user_lang(callback.from_user.id) or "ru"
    texts = _texts(lang)
    if category_id == "other":
        await callback.message.edit_text(
            build_about_text(lang),
            reply_markup=build_about_kb(),
        )
        await callback.answer()
        return
    if not category_id:
        await callback.answer(texts["error"], show_alert=False)
        return

    subcategories = load_subcategories(category_id)

    category_title = get_category_title(category_id, lang)

    if category_id in STUB_CATEGORY_IDS:
        await callback.message.edit_text(
            _stub_text(category_title, lang),
            reply_markup=build_category_stub_kb(),
        )
        await callback.answer()
        return

    if not subcategories:
        await callback.answer(texts["empty"], show_alert=False)
        return

    await callback.message.edit_text(
        f"📂 {category_title}\n\n{texts['choose']}",
        reply_markup=build_directory_subcategories_kb(category_id, subcategories, lang),
    )
    await callback.answer()