from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_directory_category_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="💇 Красота", callback_data="dir:beauty")
    kb.button(text="🚗 Транспорт", callback_data="dir:transport")
    kb.button(text="🌐 Переводы", callback_data="dir:translation")
    kb.button(text="🏠 Домашние услуги", callback_data="dir:home_services")
    kb.button(text="⚽ Спорт", callback_data="dir:sport")
    kb.button(text="🧭 Туризм", callback_data="dir:tourism")
    kb.button(text="🏡 Недвижимость", callback_data="dir:real_estate")
    kb.button(text="🏥 Здоровье", callback_data="dir:health")
    kb.button(text="📦 Повседневное", callback_data="dir:daily")
    kb.button(text="⬅️ Назад", callback_data="main:menu")
    kb.adjust(2, 1)

    return kb.as_markup()