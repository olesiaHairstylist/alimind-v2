from __future__ import annotations

from app.core.text import get_text

CATEGORY_ORDER = [
    "beauty",
    "sport",
    "health",
    "legal",
    "home",
    "kids",
    "other",
]

CATEGORY_SUBCATEGORY_ORDER: dict[str, list[str]] = {
    "beauty": ["hair", "nails", "massage", "barber"],
    "sport": ["boxing", "fitness", "swimming", "yoga"],
    "health": ["dentist", "pharmacy", "clinic", "psychology"],
    "legal": ["lawyer", "translation", "insurance", "notary"],
    "home": ["repair", "cleaning", "furniture", "appliances"],
    "kids": ["school", "tutor", "kindergarten", "activities"],
    "other": ["transport", "photographer", "pet_services", "car_rental"],
}

CATEGORY_ALIASES: dict[str, str] = {}

SUBCATEGORY_ALIASES: dict[str, str] = {
    "document_translation": "translation",
}

CATEGORY_TITLES_I18N: dict[str, dict[str, str]] = {
    "ru": {
        "beauty": "Красота",
        "sport": "Спорт",
        "health": "Здоровье",
        "legal": "Документы и право",
        "home": "Дом и ремонт",
        "kids": "Дети и обучение",
        "other": "Другое",
    },
    "en": {
        "beauty": "Beauty",
        "sport": "Sport",
        "health": "Health",
        "legal": "Documents and Law",
        "home": "Home and Repair",
        "kids": "Kids and Education",
        "other": "Other",
    },
    "tr": {
        "beauty": "Güzellik",
        "sport": "Spor",
        "health": "Sağlık",
        "legal": "Belgeler ve Hukuk",
        "home": "Ev ve Tamir",
        "kids": "Çocuklar ve Eğitim",
        "other": "Diğer",
    },
}

SUBCATEGORY_TITLES_I18N: dict[str, dict[str, str]] = {
    "ru": {
        "hair": "Волосы",
        "nails": "Ногти",
        "massage": "Массаж",
        "barber": "Барбер",
        "boxing": "Бокс",
        "fitness": "Фитнес",
        "swimming": "Плавание",
        "yoga": "Йога",
        "dentist": "Стоматолог",
        "pharmacy": "Аптека",
        "clinic": "Клиника",
        "psychology": "Психология",
        "lawyer": "Юрист",
        "translation": "Перевод",
        "document_translation": "Перевод документов",
        "insurance": "Страхование",
        "notary": "Нотариус",
        "repair": "Ремонт",
        "cleaning": "Уборка",
        "furniture": "Мебель",
        "appliances": "Техника",
        "school": "Школа",
        "tutor": "Репетитор",
        "kindergarten": "Детский сад",
        "activities": "Развитие и кружки",
        "transport": "Транспорт",
        "photographer": "Фотограф",
        "pet_services": "Услуги для животных",
        "car_rental": "Аренда авто",
    },
    "en": {
        "hair": "Hair",
        "nails": "Nails",
        "massage": "Massage",
        "barber": "Barber",
        "boxing": "Boxing",
        "fitness": "Fitness",
        "swimming": "Swimming",
        "yoga": "Yoga",
        "dentist": "Dentist",
        "pharmacy": "Pharmacy",
        "clinic": "Clinic",
        "psychology": "Psychology",
        "lawyer": "Lawyer",
        "translation": "Translation",
        "document_translation": "Document Translation",
        "insurance": "Insurance",
        "notary": "Notary",
        "repair": "Repair",
        "cleaning": "Cleaning",
        "furniture": "Furniture",
        "appliances": "Appliances",
        "school": "School",
        "tutor": "Tutor",
        "kindergarten": "Kindergarten",
        "activities": "Activities",
        "transport": "Transport",
        "photographer": "Photographer",
        "pet_services": "Pet Services",
        "car_rental": "Car Rental",
    },
    "tr": {
        "hair": "Saç",
        "nails": "Tırnak",
        "massage": "Masaj",
        "barber": "Berber",
        "boxing": "Boks",
        "fitness": "Fitness",
        "swimming": "Yüzme",
        "yoga": "Yoga",
        "dentist": "Diş Hekimi",
        "pharmacy": "Eczane",
        "clinic": "Klinik",
        "psychology": "Psikoloji",
        "lawyer": "Avukat",
        "translation": "Çeviri",
        "document_translation": "Belge Çevirisi",
        "insurance": "Sigorta",
        "notary": "Noter",
        "repair": "Tamir",
        "cleaning": "Temizlik",
        "furniture": "Mobilya",
        "appliances": "Beyaz Eşya",
        "school": "Okul",
        "tutor": "Özel Ders",
        "kindergarten": "Anaokulu",
        "activities": "Etkinlikler",
        "transport": "Ulaşım",
        "photographer": "Fotoğrafçı",
        "pet_services": "Evcil Hayvan Hizmetleri",
        "car_rental": "Araç Kiralama",
    },
}


def get_category_title(category_id: str, lang: str = "ru") -> str:
    lang = (lang or "ru").lower()
    normalized_id = CATEGORY_ALIASES.get(category_id, category_id)
    value = (
        CATEGORY_TITLES_I18N.get(lang, CATEGORY_TITLES_I18N["ru"]).get(normalized_id)
        or CATEGORY_TITLES_I18N["ru"].get(normalized_id)
    )
    return get_text(value, lang) or normalized_id


def get_subcategory_title(subcategory_id: str, lang: str = "ru") -> str:
    lang = (lang or "ru").lower()
    localized_map = SUBCATEGORY_TITLES_I18N.get(lang, SUBCATEGORY_TITLES_I18N["ru"])

    direct_value = (
        localized_map.get(subcategory_id)
        or SUBCATEGORY_TITLES_I18N["ru"].get(subcategory_id)
    )
    direct_text = get_text(direct_value, lang)
    if direct_text:
        return direct_text

    normalized_id = SUBCATEGORY_ALIASES.get(subcategory_id, subcategory_id)
    alias_value = (
        localized_map.get(normalized_id)
        or SUBCATEGORY_TITLES_I18N["ru"].get(normalized_id)
    )
    return get_text(alias_value, lang) or subcategory_id


CATEGORY_TITLES = CATEGORY_TITLES_I18N["ru"]
SUBCATEGORY_TITLES = SUBCATEGORY_TITLES_I18N["ru"]