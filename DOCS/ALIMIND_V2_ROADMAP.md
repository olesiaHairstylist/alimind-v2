ALIMIND_V2_ROADMAP.md

Статус: ACTIVE
Основание: ALIMIND_V2_GENERAL_MASTER_PLAN (LOCKED)

0. ПРАВИЛО
РАБОТА ИДЁТ СТРОГО ПО МОДУЛЯМ

Каждый модуль:

PASSPORT → IMPLEMENTATION → CHECK → LOCK → STOP
1. CURRENT SYSTEM STATE
CORE = NOT BUILT
CITY EVENTS = PARTIAL (работает, но не встроен)
DIRECTORY = NOT BUILT
CITY INFO = NOT BUILT
DATA LAYER = NEED CLEANUP
2. MODULE ORDER (СТРОГО)
MODULE_01 — CORE NAVIGATION

Статус: TODO
Приоритет: 🔴 CRITICAL

Включает:

language gate

main screen

main menu

navigation flow

back logic

Результат:
пользователь может пройти путь:
START → MENU → CATEGORY → BACK
MODULE_02 — DATA LAYER CLEANUP

Статус: TODO
Приоритет: 🔴 CRITICAL

Включает:

единый app/data/

удаление дублей

проверка путей

фиксация структуры

Результат:
один источник данных, без конфликтов
MODULE_03 — DIRECTORY

Статус: TODO
Приоритет: 🔴 HIGH

Включает:

категории

список карточек

отображение карточки

структура JSON

подключение к CORE

Результат:
каталог партнёров работает
MODULE_04 — PARTNER FLOW

Статус: TODO
Приоритет: 🔴 HIGH

Включает:

кнопка "заявка"

FSM форма

отправка в chat_id

fallback

Результат:
пользователь отправляет заявку партнёру
MODULE_05 — CITY EVENTS (FIX & CONNECT)

Статус: PARTIAL
Приоритет: 🟡 MEDIUM

Включает:

подключение к CORE

выравнивание DATA

упрощение

стабильный вывод

Результат:
события города доступны через меню
MODULE_06 — CITY INFO

Статус: TODO
Приоритет: 🟡 MEDIUM

Включает:

объявления

изменения правил

транспорт

недвижимость (snapshot)

Результат:
появляется слой городской информации
3. STOP RULE

После каждого модуля:

СТОП → ПРОВЕРКА → ФИКСАЦИЯ
4. ЗАПРЕЩЕНО

❌ делать несколько модулей сразу

❌ менять порядок

❌ добавлять функции вне модуля

❌ трогать LOCK модули


