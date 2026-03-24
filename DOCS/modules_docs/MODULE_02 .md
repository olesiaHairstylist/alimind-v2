MODULE_02_DATA_LAYER_CLEANUP_PASSPORT.md

Статус: DRAFT → (после подтверждения: LOCK)
Приоритет: 🔴 CRITICAL
Основание: ALIMIND_V2_GENERAL_MASTER_PLAN
Связанные модули: MODULE_01_CORE_NAVIGATION, CITY_EVENTS

1. НАЗНАЧЕНИЕ

MODULE_02 отвечает за:

единый и чистый слой хранения данных системы
2. ГРАНИЦЫ
Входит:

единый корень данных

единые пути чтения/записи

устранение дублей data-root

разделение боевых payload и служебных snapshot/raw данных

НЕ входит:

парсинг источников как логика бизнеса

UI-рендер

навигация

структура карточек DIRECTORY

3. ЦЕЛЬ

Система должна иметь:

1 data root
1 понятный storage path
0 дублей
4. ЕДИНЫЙ DATA ROOT

Финальный корень данных:

app/data/
 ├ city_events/
 ├ objects/
 ├ sources/
5. ПРАВИЛА DATA LAYER
5.1 Главное правило
MODULE → читает/пишет
DATA → хранит
5.2 Запрещено

data/ как параллельный корень

app/app/data/

services/app/data/ как боевой storage

хранить боевые JSON внутри модулей

смешивать raw/snapshot и боевые payload в одной папке

5.3 Разделение слоёв

app/data/city_events/ → боевые JSON для UI

app/data/objects/ → объекты/карточки

app/data/sources/ → raw/snapshot/служебные данные источников

6. CITY EVENTS STORAGE RULE

Для CITY_EVENTS боевые данные лежат только здесь:

app/data/city_events/
 ├ duty_pharmacies.json
 ├ electricity_outages.json
 ├ water_outages.json
 └ emergency_contacts.json
7. STORAGE CONTRACT
7.1 Путь к категории

Путь к JSON строится через storage layer, а не вручную в UI.

7.2 Категория → файл
PHARMACIES   → duty_pharmacies.json
ELECTRICITY  → electricity_outages.json
WATER        → water_outages.json
EMERGENCY    → emergency_contacts.json
8. READ / WRITE RULE
WRITE

Writer пишет только в единый app/data/...

READ

Reader читает только из того же единого app/data/...

Запрещено

разный путь для writer и reader

локальные Path(...) в UI, не совпадающие с storage layer

9. RAW / SNAPSHOT RULE

Snapshot и сырой слой не считаются боевым payload.

Их место:

app/data/sources/

Они не должны:

подменять боевые JSON

читаться UI напрямую

лежать рядом с итоговыми payload как равные сущности

10. ПРОБЛЕМЫ, КОТОРЫЕ ЭТОТ МОДУЛЬ УСТРАНЯЕТ

Были выявлены и признаны ошибочными:

data/ как второй корень

app/app/data/ как клон

services/app/data/ как лишний хвост

ситуация, когда writer писал в один путь, а UI/reader читал из другого

использование не того pharmacies payload

11. EDGE CASES
Если JSON отсутствует

reader возвращает None

Если payload отсутствует

UI не должен падать и обязан показывать честное сообщение:

Сейчас нет данных.
12. INVARIANTS
1. В системе существует только один боевой data root
2. UI не читает данные мимо storage layer
3. writer и reader используют один и тот же путь
4. боевые payload не смешиваются с raw/snapshot
5. дубли корней данных запрещены
13. READY CHECK

Модуль считается готовым, если:

1. существует один корень app/data/
2. дубли data-root удалены
3. writer пишет в app/data/
4. reader читает из app/data/
5. UI получает актуальные данные без падения
6. raw/snapshot не участвуют как боевые payload
7. структура совпадает с генпланом
14. ФАКТИЧЕСКИЙ РЕЗУЛЬТАТ МОДУЛЯ

На текущем этапе подтверждено:

дежурные аптеки читаются корректно

payload содержит актуальные записи, адреса и телефоны

UI показывает данные без падения

ошибка payload is None была связана с неверным data path и устранена

🔒 ФИНАЛ