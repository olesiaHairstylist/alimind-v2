ALIMIND V2 — INTERNAL SYSTEM AUDIT DOCUMENT
DATE: 2026-03-24
STATUS: ACTIVE
MODE: FACTUAL ARCHITECTURE FIXATION
PURPOSE: зафиксировать реальное внутреннее состояние проекта без фантазий, без украшений, без рефакторинга
0. СМЫСЛ ДОКУМЕНТА

Этот документ не переписывает MASTER PLAN.

Этот документ нужен для другого:

увидеть проект как он реально устроен сейчас
отделить живую архитектуру от представлений о ней
зафиксировать, что уже собрано
понять, где система соответствует плану
понять, где модуль ещё не завершён
двигаться дальше без самообмана
1. ОБЩЕЕ СОСТОЯНИЕ СИСТЕМЫ

На момент этой фиксации подтверждено:

главное меню работает
переходы работают
back navigation работает
CITY EVENTS открывается
данные читаются
JSON слой существует
scheduler-layer существует отдельно
updater существует отдельно
UI не лезет напрямую в источник
рабочая база не развалена
Вывод

ALIMIND V2 сейчас — это не набор заготовок, а уже реально собранная модульная система.

2. ФАКТИЧЕСКАЯ СТРУКТУРА ПРОЕКТА
app/
app/
  data/
    city_events/
    objects/
    sources/
    system/

  handlers/

  modules/
    city_events/
      contracts/
      feed/
      parsers/
      render/
      services/
      sources/
      storage/
      ui/

    core/
    directory/
3. ЧТО ВИДНО ПО СЛОЯМ
3.1 DATA LAYER
app/data/city_events/

Подтверждены файлы:

duty_pharmacies.json
electricity_outages.json
water_outages.json
emergency_contacts.json
Значение

Это уже реальный payload-слой модуля CITY EVENTS.

Он не смешан в один файл.
Категории разделены.
Имена читаемые.
Структура понятная.

3.2 SOURCES LAYER
app/modules/city_events/sources/

Подтверждены файлы:

asat_water_adapter.py
electricity_builder.py
electricity_fetcher.py
electricity_source.py
outages_sources.py
pharmacies_adapter.py
pharmacies_api.py
pharmacies_html_source.py
water_builder.py
water_source.py
Значение

Слой источников уже не примитивный.

Он содержит:

fetch-level
adapter-level
builder-level
source-level

Это уже pipeline, а не одиночные функции.

3.3 PARSERS LAYER
app/modules/city_events/parsers/

Подтверждены файлы:

electricity_cards.py
water_cards.py
Значение

Есть явный слой преобразования raw → user-facing format.

Parser отделён от source.

3.4 STORAGE LAYER
app/modules/city_events/storage/

Подтверждены файлы:

health_reader.py
health_writer.py
paths.py
pharmacies_snapshot_writer.py
reader.py
schema.py
writer.py
Значение

Storage оформлен как самостоятельный слой.

Внутри него уже есть:

чтение
запись
схема
пути
health storage
отдельный pharmacies snapshot writer

Это уже не MVP-хранилище.

3.5 SERVICES LAYER
app/modules/city_events/services/

Подтверждены файлы:

health_service.py
update_city_events.py
updater.py
Значение

Есть orchestration-слой.
Есть updater.
Есть системный слой наблюдения.

3.6 UI LAYER
app/modules/city_events/ui/

Подтверждены файлы:

callbacks.py
handlers.py
router.py
Значение

UI изолирован в модуле.
UI не смешан с source.
UI не смешан с storage.

4. ГЛАВНЫЙ ФАКТ ОБ АРХИТЕКТУРЕ

По факту проект уже живёт по цепочке:

sources → parsers → storage → services → UI

И отдельно:

data/ = финальные JSON payloads
sources/ = raw / source layer
Ключевой вывод

Архитектура не распалась.
Основной каркас системы удержан.

5. CITY EVENTS — РЕАЛЬНОЕ СОСТОЯНИЕ ПО КАТЕГОРИЯМ
5.1 ELECTRICITY
Статус

Наиболее цельно собранная линия из просмотренных.

Подтверждённый жизненный цикл
официальный endpoint
→ POST request
→ raw list[dict]
→ optional raw snapshot
→ parser
→ compact outage cards
→ payload
→ electricity_outages.json
→ UI read
→ render
→ пользовательский вывод
Что реально подтверждено
Источник

Есть живой HTTP POST на официальный endpoint:

https://www.akdenizedas.com.tr/elektrik-getir
Raw storage

Есть raw snapshot:

app/data/sources/electricity_raw.json
Parser

electricity_cards.py:

работает через plannedOutage
фильтрует только ANTALYA / ALANYA
пропускает записи без startDateTime
извлекает area из большого message
собирает компактные карточки:
title
details
address
phone
Финальный payload

Пишется в:

app/data/city_events/electricity_outages.json
UI path

UI читает payload через read_payload(...)
и отдаёт в render-слой.

Вывод по electricity

Electricity — это полноценный модульный data pipeline.
Это уже не заготовка и не кусок кода.

5.2 WATER
Статус

Архитектурно встроен правильно, но источник пока временный.

Подтверждённый жизненный цикл
water_raw.json
→ load_raw()
→ parse_water_items(...)
→ build_payload(...)
→ water_outages.json
→ UI read
→ render
→ пользовательский вывод
Что реально подтверждено
Источник

water_source.py пока не делает реальный сетевой запрос.
Он читает локальный raw-файл:

app/data/sources/water_raw.json
Значение

Water source сейчас — stub / temporary source implementation.

Parse/build layer

Внутренний build-поток:

читает raw
извлекает:
title
area
start_at
end_at
note
address
формирует карточки:
title
details
address
phone
Дата-фильтр

В коде есть заготовка фильтра по дате, но она отключена.

Финальный payload

Пишется в:

app/data/city_events/water_outages.json
Вывод по water

Water — рабочая пользовательская линия, но не финальный source layer.

То есть незавершён здесь не UI и не payload, а именно:

SOURCE REALIZATION
5.3 PHARMACIES
Статус

Самая сложная линия внутри CITY EVENTS из просмотренных.

Что реально вскрыто
Есть как минимум две линии получения данных
Линия A — JSON/API

Через adapter:

adapt_pharmacies_raw(raw_json, source_region_id)

Эта линия:

работает с raw_json["data"]
извлекает:
EczaneID
EczaneAdi
EczaneILCE
отбрасывает битые записи
формирует нормализованные технические записи:
{
  "source_region_id": ...,
  "pharmacy_id": ...,
  "name": ...,
  "district": ...,
}
Линия B — HTML source

Через публичную страницу:

https://www.alanyaeo.org.tr/tr/nobetci-eczaneler

HTML-линия:

делает GET
парсит текст страницы
находит блок Nöbetçi Eczane Listesi
выделяет region
выделяет pharmacy name
выделяет phone
выделяет address
собирает пользовательски полезные items
Что это значит

Pharmacies — это уже не простое “событие”, а специализированный подмодуль с несколькими способами получения данных.

Чего пока не подтверждено до конца

Мы ещё не увидели полное финальное звено:

SOURCE / ADAPTER → duty_pharmacies.json → UI final read

То есть pharmacies почти раскрыты, но не закрыты на 100% до финального JSON-потока в этой сессии.

Вывод по pharmacies

Pharmacies — самый нетривиальный подмодуль в CITY EVENTS.
Он уже несёт в себе:

fallback nature
multi-source thinking
структуру, близкую к каталоговым сущностям
6. UI PATH — РЕАЛЬНОЕ СОСТОЯНИЕ

Подтверждено:

menu открывается
category open handlers есть
category payload читается через read_payload(DATA_DIR, category)
если payload отсутствует, показывается честное:
Данные пока недоступны.
длинные списки режутся до 15 записей
render идёт через отдельный слой:
render_category_payload(...)
Главный вывод

UI работает от готового payload.
UI не знает ничего о:

requests
HTML
raw
парсерах
endpoint-ах

Это архитектурно сильное место проекта.

7. HEALTH LAYER — РЕАЛЬНОЕ СОСТОЯНИЕ
Что подтверждено

Health-слой уже существует в структуре модуля:

contracts/
  source_health_contracts.py

storage/
  health_reader.py
  health_writer.py

services/
  health_service.py
Что это значит

Health уже не идея.
Это уже оформленный слой:

contracts
storage
services
Но честный статус

Health-поток пока не закрыт полностью как законченный модуль.

Состояние честнее описывается так:

MODULE_04 — PARTIALLY IMPLEMENTED

или подробнее:

структура есть
базовая логика есть
интеграция в updater обсуждена и частично подготовлена
smoke verification не подтверждена как завершённая
category-aware semantics ещё не внедрены
8. ОЧЕНЬ ВАЖНОЕ АРХИТЕКТУРНОЕ НАБЛЮДЕНИЕ

В процессе разбора было выявлено принципиальное различие категорий по смыслу EMPTY.

Pharmacies

Пустота скорее выглядит как аномалия.

Electricity

Пустота может быть полностью валидным состоянием.

Water

Семантика пока не зафиксирована окончательно, зависит от реального источника.

Значение

Система пока начинает различать:

success
empty
fail

Но ещё не обучена понимать пустоту по смыслу категории.

Это не срочная задача на сейчас.
Это важное наблюдение для будущей revision-логики.

9. ЧТО УДАЛОСЬ ПОНЯТЬ ПО ПРОЕКТУ В ЦЕЛОМ
9.1 Проект не хаотичен

Снаружи он мог казаться местами тяжёлым, но изнутри видно:
это не куча файлов, а настоящая система слоёв.

9.2 Архитектура удержана

Главный поток не сломан:

source не в UI
parser не в кнопках
data не смешаны в одном месте
JSON слой существует отдельно
9.3 Проект уже вышел из стадии “набросок”

Сейчас это уже не бумажная идея и не MVP на коленке.

Это состояние:

WORKING MODULAR SYSTEM
9.4 Самый сильный модуль сейчас

Из просмотренного:

strongest complete line: ELECTRICITY
9.5 Самый незавершённый участок

Не по интерфейсу, а по смыслу:

WATER SOURCE REALIZATION
9.6 Самый сложный подмодуль
PHARMACIES
10. СВЕРКА С MASTER PLAN — ЧЕСТНЫЙ ВЫВОД

По факту, после внутреннего просмотра, можно зафиксировать:

Система НЕ ушла в сторону от MASTER PLAN

Она:

следует модульной логике
держит JSON data layer
изолирует UI от источников
живёт через categories
работает через updater/scheduler, а не через прямой UI fetch
Но

Некоторые модули уже начали углубляться сильнее, чем это видно из общего плана.

Это не нарушение.
Это признак того, что проект начал жить в коде, а не только в структуре документа.

11. ЧТО НЕЛЬЗЯ ДЕЛАТЬ ПОСЛЕ ЭТОЙ ФИКСАЦИИ

После такого просмотра нельзя:

резко упрощать модульную структуру
начинать массовый перенос файлов
смешивать UI и source “для удобства”
открывать сразу новые модули без закрытия понимания текущих
делать ложный вывод “проект переусложнён, надо всё свернуть”

Потому что изнутри как раз видно обратное:

система держится

12. ЧТО МОЖНО СЧИТАТЬ ТЕКУЩИМ РЕАЛЬНЫМ СТАТУСОМ
ALIMIND V2

GENERAL STATUS:
STABLE BASE

ARCHITECTURE:
CONSISTENT AND MODULAR

CITY EVENTS:
WORKING SYSTEM

ELECTRICITY:
FULLY TRACEABLE PIPELINE

WATER:
WORKING PIPELINE WITH TEMP SOURCE STUB

PHARMACIES:
MULTI-SOURCE SUBMODULE, PARTIALLY TRACEABLE TO FINAL OUTPUT

HEALTH:
STRUCTURE EXISTS, MODULE NOT FULLY CLOSED
13. ГЛАВНЫЙ ИТОГ

ALIMIND V2 на этой стадии — это уже не “давай сделаем бота”.

Это:

рабочая платформа
с живым data layer
с реальным city module
с модульным разложением
с возможностью безопасно наращивать систему

Самое важное:
проект не нужно “спасать”.
Его нужно понимать, фиксировать и развивать без суеты.

14. ФИНАЛЬНАЯ ФОРМУЛА СОСТОЯНИЯ
ALIMIND V2

Система не идеальна.
Система не завершена.
Но система уже настоящая.
И главное — она не развалена.
Она держит форму.

Если хотите, следующим сообщением я
соберу из этого ещё более жёсткую LOCK-версию документа в вашем стиле — коротко, сухо, как внутренний паспорт состояния.

City events  закрываем 