ALIMIND V2 — ROADMAP (REAL STATE)

Статус: ACTIVE
Основание: ФАКТИЧЕСКОЕ СОСТОЯНИЕ ПРОЕКТА (2026-03-24)

0. ПРАВИЛО

РАБОТА ИДЁТ СТРОГО ПО МОДУЛЯМ

Каждый модуль:

PASSPORT → IMPLEMENTATION → CHECK → LOCK → STOP

Никаких параллельных изменений.
Никакого “добавим по пути”.

1. CURRENT SYSTEM STATE (РЕАЛЬНОСТЬ)
CORE

Статус: PARTIAL (базовый слой есть)

Есть:

handlers/start.py
базовый вход
начальная навигация

Нет:

полной системы меню (config → validator → builder)
финального navigation flow
системного back control
CITY EVENTS

Статус: IMPLEMENTED (PARTIAL+)

Фактически уже есть модуль:

app/modules/city_events/
  contracts/
  feed/
  parsers/
  render/
  services/
  sources/
  storage/
  ui/

Также есть:

scheduler (MODULE_03 — LOCKED)
updater
systemd service + timer
last good snapshot логика

Но:

не интегрирован полностью в CORE
нет health-layer (уже начат — MODULE_04)
нет финального UI поведения
есть риски в data-структуре
DATA LAYER

Статус: НЕСТАБИЛЕН

Есть:

app/data/
city_events
objects
sources

Проблема:

нет жёсткого разделения:
public data
system data
source adapters
возможна путаница sources (data vs module)
DIRECTORY

Статус: NOT STARTED

PARTNER FLOW

Статус: NOT STARTED

CITY INFO

Статус: NOT STARTED

2. КЛЮЧЕВОЕ ПЕРЕОСМЫСЛЕНИЕ

Старый roadmap больше не актуален.

Причина:

👉 CITY EVENTS уже реализован как модуль
👉 scheduler уже существует
👉 архитектура уже многослойная

Нельзя идти “с нуля”.
Нужно достраивать и стабилизировать.

3. АКТУАЛЬНЫЙ ПОРЯДОК МОДУЛЕЙ

(СТРОГО)

MODULE_01 — CORE NAVIGATION BASELINE

Статус: IN PROGRESS
Приоритет: 🔴 CRITICAL

Цель

Собрать стабильный навигационный слой системы.

Включает:
language gate (если нужен — финализировать)
main screen
main menu (config → validator → builder)
navigation flow
back logic (единый)
точку входа /start
Результат:

👉 стабильная навигация
👉 все модули подключаются через CORE
👉 UI перестаёт быть хаотичным

MODULE_02 — DATA LAYER NORMALIZATION

Статус: TODO
Приоритет: 🔴 CRITICAL

Цель

Убрать хаос в app/data/

Включает:

Жёсткое разделение:

data/public/
data/system/
data/objects/

Удаление конфликтов:

sources (data vs module)
дубли путей
неочевидные JSON

Фиксация:

где лежат snapshot
где лежит health
где лежат объекты
Результат:

👉 один понятный data-слой
👉 отсутствие путаницы
👉 стабильная база для всех модулей

MODULE_03 — CITY EVENTS (STABILIZATION & CONNECT)

Статус: PARTIAL
Приоритет: 🔴 HIGH

Цель

Довести CITY EVENTS до полноценного системного модуля.

Включает:
подключение к CORE navigation
финализация feed
выравнивание render
проверка storage
единый вход через UI
устранение лишней сложности
Важно:

НЕ переписывать с нуля
ТОЛЬКО стабилизировать

Результат:

👉 CITY EVENTS работает как часть системы
👉 доступен через меню
👉 не ломает UI

MODULE_04 — SOURCE HEALTH & ERROR CLASSIFICATION

Статус: IN PROGRESS
Приоритет: 🔴 HIGH

Уже сделано:
LOCK document
STEP_1 (data structure)
Дальше:
STEP_2 — reader/writer
STEP_3 — интеграция в updater
STEP_4 — логика обновления health
Цель:

👉 система понимает, что происходит с источниками

Результат:

👉 нет “немых” ошибок
👉 есть честная диагностика

MODULE_05 — DIRECTORY (CATALOG SYSTEM)

Статус: TODO
Приоритет: 🟡 MEDIUM

Включает:
категории
список объектов
карточка объекта
JSON структура
интеграция в CORE
Результат:

👉 появляется каталог партнёров

MODULE_06 — PARTNER FLOW

Статус: TODO
Приоритет: 🟡 MEDIUM

Включает:
кнопка "заявка"
FSM
отправка партнёру (chat_id)
fallback
Результат:

👉 пользователь может взаимодействовать с бизнесом

MODULE_07 — CITY INFO

Статус: TODO
Приоритет: 🟡 MEDIUM

Включает:
объявления
изменения правил
транспорт
недвижимость (snapshot)
Результат:

👉 появляется информационный слой города

4. STOP RULE

После каждого модуля:

СТОП → ПРОВЕРКА → ФИКСАЦИЯ → LOCK

5. ЗАПРЕЩЕНО

❌ идти по старому roadmap
❌ переписывать рабочие модули
❌ смешивать data/system/public
❌ добавлять функции вне текущего модуля
❌ трогать LOCK модули
❌ чинить всё сразу

6. ТЕКУЩАЯ ТОЧКА

Сейчас система находится здесь:

👉 MODULE_01 — CORE NAVIGATION (в процессе)
👉 MODULE_04 — начат (structure зафиксирована)

7. СЛЕДУЮЩИЙ ШАГ

СТРОГО:

👉 
завершить MODULE_01
или
👉 
перейти в MODULE_04_STEP_2 (если сознательно фокус на backend)

8. ГЛАВНЫЙ ПРИНЦИП

Система уже построена на 40–50%.

Теперь задача:

👉 не строить заново
👉 а стабилизировать и связать