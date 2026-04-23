from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.modules.core.language.service import get_user_lang

router = Router()

PHRASEBOOK_MENU_CB = "phrasebook:menu"
PHRASEBOOK_CAT_CB_PREFIX = "phrasebook:cat:"


RU_TO_TR = {
    "restaurant": {
        "title": "🍽 Ресторан",
        "items": [
            ("Merhaba", "Здравствуйте", "мерхаба"),
            ("Menü alabilir miyim?", "Можно меню?", "меню алабилир мийим"),
            ("Su alabilir miyim?", "Можно воду?", "су алабилир мийим"),
            ("Bu nedir?", "Что это?", "бу недир"),
            ("Tuvalet nerede?", "Где туалет?", "тувалет нереде"),
            ("Hesap lütfen", "Счёт, пожалуйста", "хесап лютфен"),
            ("Çok lezzetli", "Очень вкусно", "чок леззетли"),
            ("Teşekkür ederim", "Спасибо", "тешеккюр эдерим"),
        ],
    },
    "taxi": {
        "title": "🚕 Такси",
        "items": [
            ("Merhaba", "Здравствуйте", "мерхаба"),
            ("Buraya gider misiniz?", "Можете отвезти сюда?", "бурая гидер мисиниз"),
            ("Haritada göstereyim", "Я покажу на карте", "харитада гёстерейим"),
            ("Ne kadar sürer?", "Сколько времени займёт?", "не кадар сюрер"),
            ("Ne kadar?", "Сколько стоит?", "не кадар"),
            ("Burada durun lütfen", "Остановите здесь, пожалуйста", "бурада дурун лютфен"),
            ("Bir dakika", "Одну минуту", "бир дакыка"),
            ("Çok pahalı", "Очень дорого", "чок пахалы"),
        ],
    },
    "pharmacy": {
        "title": "🏥 Аптека",
        "items": [
            ("Merhaba", "Здравствуйте", "мерхаба"),
            ("Başım ağrıyor", "У меня болит голова", "башым арыйор"),
            ("Midem ağrıyor", "У меня болит желудок", "мидем арыйор"),
            ("Ateşim var", "У меня температура", "атешим вар"),
            ("Soğuk algınlığı için ilaç var mı?", "Есть лекарство от простуды?", "соок алгынлыгы ичин иляч вар мы"),
            ("Ağrı kesici var mı?", "Есть обезболивающее?", "агры кесиджи вар мы"),
            ("Reçetesiz olur mu?", "Можно без рецепта?", "речетесиз олур му"),
            ("Nasıl kullanılır?", "Как это принимать?", "насыл кулланылыр"),
        ],
    },
    "shop": {
        "title": "🛍 Магазин",
        "items": [
            ("Bu ne kadar?", "Сколько это стоит?", "бу не кадар"),
            ("Daha ucuzu var mı?", "Есть подешевле?", "даха уджузу вар мы"),
            ("Şunu gösterebilir misiniz?", "Покажите вот это", "шуну гёстеребилир мисиниз"),
            ("Başka beden var mı?", "Есть другой размер?", "башка беден вар мы"),
            ("Deneyebilir miyim?", "Можно примерить?", "денейебилир мийим"),
            ("Kartla ödeyebilir miyim?", "Можно оплатить картой?", "картла одейебилир мийим"),
            ("Poşet alabilir miyim?", "Можно пакет?", "пошет алабилир мийим"),
            ("Teşekkür ederim", "Спасибо", "тешеккюр эдерим"),
        ],
    },
    "communication": {
        "title": "🤝 Общение",
        "items": [
            ("Merhaba", "Здравствуйте", "мерхаба"),
            ("Nasılsınız?", "Как вы?", "насылсыныз"),
            ("Anlamıyorum", "Я не понимаю", "анламыйорум"),
            ("Ben anlamadım", "Я не понял", "бен анламадым"),
            ("Yavaş konuşur musunuz?", "Говорите медленнее, пожалуйста", "яваш конушур мусунуз"),
            ("Tekrar eder misiniz?", "Повторите, пожалуйста", "текрар эдер мисиниз"),
            ("Yardım eder misiniz?", "Помогите, пожалуйста", "ярдым эдер мисиниз"),
            ("Türkçe bilmiyorum", "Я не знаю турецкий", "тюркче бильмийорум"),
        ],
    },
}
TR_TO_RU = {
    "greeting": {
        "title": "👋 Karşılama",
        "items": [
            ("Здравствуйте", "Merhaba", "zdravstvuyte"),
            ("Добро пожаловать", "Hoş geldiniz", "dobro pozhalovat"),
            ("Как дела?", "Nasılsınız?", "kak dela"),
            ("Чем могу помочь?", "Nasıl yardımcı olabilirim?", "chem mogu pomoch"),
            ("Что вам нужно?", "Neye ihtiyacınız var?", "chto vam nuzhno"),
            ("Подождите минуту", "Bir dakika bekleyin", "podozhdite minutu"),
            ("Спасибо", "Teşekkür ederim", "spasibo"),
        ],
    },
    "service": {
        "title": "💰 Satış / Servis",
        "items": [
            ("Чем могу помочь?", "Nasıl yardımcı olabilirim?", "chem mogu pomoch"),
            ("Что вы ищете?", "Ne arıyorsunuz?", "chto vy ishchete"),
            ("Что вам нужно?", "Neye ihtiyacınız var?", "chto vam nuzhno"),
            ("Какой размер вам нужен?", "Hangi beden lazım?", "kakoy razmer vam nuzhen"),
            ("Какой цвет вы хотите?", "Hangi rengi istiyorsunuz?", "kakoy tsvet vy khotite"),
            ("Сколько стоит?", "Ne kadar?", "skolko stoit"),
            ("Оплата картой или наличными?", "Kart mı nakit mi?", "oplata kartoy ili nalichnymi"),
            ("Это хорошее качество", "Bu kaliteli", "eto khoroshee kachestvo"),
            ("Хотите посмотреть?", "Bakmak ister misiniz?", "khotite posmotret"),
            ("Хотите примерить?", "Denemek ister misiniz?", "khotite primerit"),
        ],
    },
    "cafe": {
        "title": "☕ Kafe / Restoran",
        "items": [
            ("Что будете заказывать?", "Ne alırsınız?", "chto budete zakazyvat"),
            ("Что вы хотите кушать?", "Ne yemek istersiniz?", "chto vy khotite kushat"),
            ("Что вы будете пить?", "Ne içersiniz?", "chto vy budete pit"),
            ("Вам острое?", "Acılı olur mu?", "vam ostroe"),
            ("Вам с собой или здесь?", "Paket mi burada mı?", "vam s soboy ili zdes"),
            ("Хотите чай или кофе?", "Çay mı kahve mi istersiniz?", "khotite chay ili kofe"),
            ("Ещё что-нибудь?", "Başka bir şey?", "eshchyo chto nibud"),
            ("Приятного аппетита", "Afiyet olsun", "priyatnogo appetita"),
            ("Минуту, пожалуйста", "Bir dakika lütfen", "minutu pozhaluysta"),
            ("Счёт, пожалуйста", "Hesap lütfen", "schyot pozhaluysta"),
        ],
    },
    "taxi": {
        "title": "🚖 Taksi",
        "items": [
            ("Куда вам нужно?", "Nereye gitmeniz gerekiyor?", "kuda vam nuzhno"),
            ("Куда едем?", "Nereye gidiyoruz?", "kuda yedem"),
            ("Покажите на карте", "Haritada gösterin", "pokazhite na karte"),
            ("Напишите адрес", "Adresi yazın", "napishite adres"),
            ("Здесь?", "Buraya mı?", "zdes"),
            ("Здесь остановить?", "Burada durayım mı?", "zdes ostanovit"),
            ("Сколько стоит?", "Ne kadar?", "skolko stoit"),
            ("Дорога платная", "Yol ücretli", "doroga platnaya"),
            ("Далеко?", "Uzak mı?", "daleko"),
            ("Подождите минуту", "Bir dakika bekleyin", "podozhdite minutu"),
        ],
    },
    "communication": {
        "title": "🤝 İletişim",
        "items": [
            ("Я не понимаю", "Anlamıyorum", "ya ne ponimayu"),
            ("Повторите, пожалуйста", "Tekrar eder misiniz?", "povtorite pozhaluysta"),
            ("Говорите медленно", "Yavaş konuşun", "govorite medlenno"),
            ("Что вы сказали?", "Ne dediniz?", "chto vy skazali"),
            ("Покажите, пожалуйста", "Gösterin lütfen", "pokazhite pozhaluysta"),
            ("Напишите, пожалуйста", "Yazar mısınız lütfen?", "napishite pozhaluysta"),
            ("Подождите", "Bekleyin", "podozhdite"),
            ("Сейчас", "Şimdi", "seychas"),
            ("Хорошо", "Tamam", "khorosho"),
            ("Спасибо", "Teşekkür ederim", "spasibo"),
        ],
    },
}


def _build_phrasebook_menu_kb(lang: str):
    b = InlineKeyboardBuilder()

    if lang == "ru":
        b.button(text="🍽 Ресторан", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}restaurant")
        b.button(text="🚕 Такси", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}taxi")
        b.button(text="🏥 Аптека", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}pharmacy")
        b.button(text="🛍 Магазин", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}shop")
        b.button(text="🤝 Общение", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}communication")
    elif lang == "tr":
        b.button(text="👋 Karşılama", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}greeting")
        b.button(text="💰 Satış / Servis", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}service")
        b.button(text="☕ Kafe / Restoran", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}cafe")
        b.button(text="🚖 Taksi", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}taxi")
        b.button(text="🤝 İletişim", callback_data=f"{PHRASEBOOK_CAT_CB_PREFIX}communication")

    b.button(
        text="🏠 В главное меню" if lang == "ru" else "🏠 Ana menü",
        callback_data="main:menu",
    )
    b.adjust(1)
    return b.as_markup()


def _build_phrasebook_back_kb(lang: str):
    b = InlineKeyboardBuilder()
    b.button(
        text="⬅️ Назад" if lang == "ru" else "⬅️ Geri",
        callback_data=PHRASEBOOK_MENU_CB,
    )
    b.button(
        text="🏠 В главное меню" if lang == "ru" else "🏠 Ana menü",
        callback_data="main:menu",
    )
    b.adjust(1)
    return b.as_markup()


def _render_phrasebook_menu_text(lang: str) -> str:
    if lang == "ru":
        return "🗣 Разговорник\n\nВыберите ситуацию:"
    if lang == "tr":
        return "🗣 Konuşma kalıpları\n\nBir durum seçin:"
    return "This feature is focused on RU/TR communication for now."


def _render_category_text(lang: str, category_id: str) -> str:
    if lang == "ru":
        category = RU_TO_TR.get(category_id)
        if not category:
            return "Раздел не найден"

        lines = [category["title"], ""]
        for i, (original, translated, pronunciation) in enumerate(category["items"], start=1):
            lines.append(f"{i}. <b>{original}</b>")
            lines.append(f"— {translated}")
            lines.append(f"— <i>{pronunciation}</i>")
            lines.append("")
        return "\n".join(lines).strip()

    if lang == "tr":
        category = TR_TO_RU.get(category_id)
        if not category:
            return "Bölüm bulunamadı"

        lines = [category["title"], ""]
        for i, (original, translated, pronunciation) in enumerate(category["items"], start=1):
            lines.append(f"{i}. <b>{original}</b>")
            lines.append(f"— {translated}")
            lines.append(f"— <i>{pronunciation}</i>")
            lines.append("")
        return "\n".join(lines).strip()

    return "This feature is focused on RU/TR communication for now."


@router.callback_query(F.data == PHRASEBOOK_MENU_CB)
async def open_phrasebook_menu(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id) or "ru"

    text = _render_phrasebook_menu_text(lang)
    kb = _build_phrasebook_menu_kb(lang)

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data.startswith(PHRASEBOOK_CAT_CB_PREFIX))
async def open_phrasebook_category(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id) or "ru"
    category_id = callback.data.removeprefix(PHRASEBOOK_CAT_CB_PREFIX)

    text = _render_category_text(lang, category_id)
    kb = _build_phrasebook_back_kb(lang)

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

    await callback.answer()