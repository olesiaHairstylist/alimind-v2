ALIMIND V2 — MODULE_01 LOCK DOCUMENT

MODULE: CORE NAVIGATION
DATE: 2026-03-23
STATUS: 🔒 LOCK
MODE: STABLE

1. ЦЕЛЬ МОДУЛЯ

Создать базовый входной слой системы:

единая точка входа /start
навигация по системе
возврат в главное меню
первичный выбор языка
2. РЕАЛИЗОВАНО
2.1 ENTRY FLOW
/start
→ LANGUAGE GATE
→ MAIN MENU
2.2 LANGUAGE GATE

Экран:

Выберите язык / Select language

Кнопки:

🇷🇺 Русский → lang:ru
🇬🇧 English → lang:en
🇹🇷 Türkçe → lang:tr
2.3 LANGUAGE STORAGE (TEMP)
user_lang: dict[int, str] = {}

user_lang[user_id] = "ru/en/tr"
хранение в памяти
без БД
без персистентности
2.4 MAIN MENU

Кнопки:

🏙 События города → main:city_events
🛠 Услуги → main:directory
ℹ️ Информация → main:info
2.5 NAVIGATION

Реализовано:

переходы через callback_data
возврат через main:menu
единая функция:
show_main_menu()
2.6 ROUTING

Все обработчики подключены через router

dp.include_router(start_router)
dp.include_router(language_router)
dp.include_router(directory_router)
dp.include_router(city_events_router)
3. ИНВАРИАНТЫ (ЗАПРЕЩЕНО НАРУШАТЬ)
3.1 ENTRY POINT
только main.py
3.2 ROUTING
нет "свободных" хендлеров
только через router
3.3 LANGUAGE GATE
всегда вызывается через /start
не ломает другие модули
3.4 MAIN MENU
единая точка возврата
не дублируется
3.5 CALLBACK STRUCTURE
lang:*
main:*
4. ОГРАНИЧЕНИЯ (ОСОЗНАННЫЕ)
❌ нет перевода интерфейса
❌ нет БД
❌ нет авто-пропуска языка
❌ нет сохранения между сессиями
5. ПРОВЕРКА (SMOKE TEST)
Сценарий 1
/start → выбор языка → главное меню → 🏙 События города
Сценарий 2
/start → выбор языка → главное меню → назад → меню
Сценарий 3
/start → выбор языка → главное меню → 🛠 Услуги

👉 Все сценарии проходят без ошибок

6. РЕЗУЛЬТАТ

Система получила:

стабильный входной слой
контролируемую навигацию
единый main menu
базовую точку расширения (язык)
7. СТАТУС
MODULE_01 — CORE NAVIGATION

✔ navigation flow
✔ back logic
✔ main menu
✔ language gate

STATUS: LOCKED 🔒
8. СЛЕДУЮЩИЙ ШАГ

Рекомендуется:

👉 MODULE_02 / MODULE_03 (по текущему roadmap)

развитие функциональных модулей
или
подготовка language layer (позже, без спешки)

Если хотите — дальше идём по плану и я уже буду держать вас в режиме системы, а не хаоса.
city_events/
  sources/
    electricity_source.py
    asat_water_adapter.py

  parsers/
    electricity_cards.py
    water_cards.py

  storage/
    reader.py
    writer.py
    schema.py

  render/
    text_render.py

  data/
    electricity_outages.json
    water_outages.json
    emergency_contacts.json