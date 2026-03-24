MODULE: CITY_EVENTS
DATE: 2026-03-23
STATUS: 🔒 LOCK
MODE: STABLE

1. ЦЕЛЬ МОДУЛЯ

Предоставить пользователю актуальные городские данные в едином формате:

отключения электричества
отключения воды
экстренные службы
дежурные аптеки

Модуль должен работать независимо от UI и обеспечивать стабильный поток данных:

источник → обработка → хранение → отображение
2. РЕАЛИЗОВАНО
2.1 ELECTRICITY
source → raw → parser → payload → bot
источник: Akdeniz EDAŞ
получение JSON
парсинг через parsers/electricity_cards.py
сборка payload → electricity_outages.json
2.2 WATER
source(html) → parser → payload → bot
источник: ASAT
получение HTML
парсинг через parsers/water_cards.py
запись напрямую в water_outages.json
2.3 EMERGENCY
static json → reader → bot
статический файл
emergency_contacts.json
без источника и парсинга
2.4 PHARMACIES
payload → reader → bot
готовый JSON
без динамического источника (на текущем этапе)
3. СТРУКТУРА МОДУЛЯ
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
4. ИНВАРИАНТЫ (ЗАПРЕЩЕНО НАРУШАТЬ)
UI не знает имён файлов
чтение данных только через storage/reader.py
соответствие category → file только через mapping
render не занимается парсингом
sources не занимаются отображением
parsers не пишут файлы напрямую
все финальные данные лежат в:
app/data/city_events/
5. ПУСТОЕ СОСТОЯНИЕ (EMPTY STATE)

Если источник не даёт данных:

бот показывает честное сообщение:
"Плановых отключений не найдено"

Запрещено:

подставлять фиктивные данные
скрывать отсутствие данных
6. ИСТОЧНИКИ ДАННЫХ
electricity → Akdeniz EDAŞ
water → ASAT
emergency → локальные данные
pharmacies → локальный payload
7. ОГРАНИЧЕНИЯ (ОСОЗНАННЫЕ)
обновление запускается вручную
water зависит от HTML структуры ASAT
parser electricity использует упрощённый разбор message
pharmacies не имеют живого источника
нет кэширования
нет fallback-логики при ошибках
8. ПРОВЕРКА (SMOKE TEST)

Сценарии:

меню → electricity → отображаются актуальные данные
меню → water → либо данные, либо честное пустое состояние
меню → emergency → список телефонов
меню → pharmacies → список аптек
везде работает возврат назад

👉 все сценарии проходят без ошибок

9. РЕЗУЛЬТАТ

Система получила:

единый слой городских данных
разделение на источники / парсеры / хранение / отображение
стабильную работу без зависимости от UI
готовность к автоматизации
10. СТАТУС
MODULE_02 — CITY_EVENTS

✔ electricity — live
✔ water — live
✔ emergency — static
✔ pharmacies — static

STATUS: LOCKED 🔒