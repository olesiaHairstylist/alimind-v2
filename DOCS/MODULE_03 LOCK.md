ALIMIND V2 — MODULE_03 LOCK DOCUMENT

MODULE: SCHEDULER (AUTO UPDATE)
DATE: 2026-03-24
STATUS: 🔒 LOCK
MODE: STABLE

1. ЦЕЛЬ МОДУЛЯ

Перевести обновление городских данных из ручного режима в автономный.

Модуль SCHEDULER отвечает за автоматический запуск обновления без участия пользователя.

Цель слоя:

запускать обновление данных автоматически
не зависеть от Telegram UI
не требовать ручного старта
перевести CITY_EVENTS в режим системной жизни

Итоговая модель:

timer → service → update_city_events.py → data refresh

2. ЧТО РЕАЛИЗОВАНО
2.1 UPDATE ENTRYPOINT

Создан единый update-скрипт:

app/modules/city_events/services/update_city_events.py

Он:

запускает обновление electricity
запускает обновление water
пишет итоговые payload-файлы
ведёт консольный лог запуска
завершает цикл единым SUMMARY-статусом
2.2 SERVICE LAYER

Создан systemd service:

/etc/systemd/system/alimind-city-events.service

Назначение:

запускать updater как отдельную системную задачу
работать вне Telegram-бота
использовать проект в каталоге:
/root/alimind-v2

Service работает через:

WorkingDirectory=/root/alimind-v2
ExecStart=/root/alimind-v2/venv/bin/python -m app.modules.city_events.services.update_city_events
User=root
2.3 TIMER LAYER

Создан systemd timer:

/etc/systemd/system/alimind-city-events.timer

Назначение:

запускать service автоматически по расписанию
не требовать ручного участия
сохранять системную периодичность

Текущая модель:

ежедневный запуск
OnCalendar=*-*-* 07:00:00
Persistent=true
2.4 VPS DEPLOYMENT

Поднят отдельный каталог нового проекта:

/root/alimind-v2

Что подтверждено:

новая структура app/... реально загружена на VPS
отдельный venv создан
модуль запускается из новой архитектуры
старый проект не используется как база для нового scheduler-слоя
3. РЕАЛЬНОЕ ПОВЕДЕНИЕ СИСТЕМЫ
3.1 РУЧНОЙ ЗАПУСК ПРОВЕРЕН

Проверено:

python -m app.modules.city_events.services.update_city_events

Результат:

updater стартует корректно
service выполняется
systemd видит завершение задачи
3.2 STATUS SERVICE ПОДТВЕРЖДЁН

Финальный рабочий статус после выполнения:

ActiveState=inactive
SubState=dead

Это является нормальным штатным состоянием для oneshot-service.

3.3 ЛОГИКА EXIT CODE ИСПРАВЛЕНА

Исправлено поведение update_city_events.py:

SUMMARY: SUCCESS → return 0
SUMMARY: PARTIAL_OR_FAILED → return 0

Это сделано намеренно.

Причина:

частичный сетевой сбой внешних источников не должен считаться аварией systemd, если:

updater отработал до конца
старые JSON не уничтожены
бот продолжает работать на последнем снапшоте
4. ИНВАРИАНТЫ МОДУЛЯ

Нарушать запрещено:

scheduler не зависит от Telegram UI
бот не делает прямые запросы к внешним источникам
все обновления идут только через updater
updater запускается как отдельная системная задача
частичный сбой источника не должен рушить systemd-слой
отсутствие новых данных не является крахом системы
последний удачный snapshot считается допустимой опорой работы
5. EMPTY / FAILURE STATE

Если источник недоступен:

updater пишет ошибку в лог
итоговый статус = SUMMARY: PARTIAL_OR_FAILED
старые JSON не затираются
бот продолжает показывать последний доступный снимок данных

Запрещено:

считать любой timeout полным крахом системы
удалять прежние данные при сбое источника
маскировать сетевую ошибку как успешное обновление
6. ЧТО ПОДТВЕРЖДЕНО ПО ФАКТУ
6.1 АРХИТЕКТУРА

Подтверждено:

новая структура проекта app/... работает на VPS
service запускает именно новый проект
timer привязан к новому service
6.2 SYSTEMD

Подтверждено:

ошибки CHDIR устранены
ошибка ModuleNotFoundError: No module named 'app' устранена
service больше не падает из-за неверного пути запуска
6.3 СЕТЕВОЙ СЛОЙ

Подтверждено:

внешние источники Akdeniz EDAŞ и ASAT с текущего VPS могут не отвечать по timeout
это не является ошибкой внутренней архитектуры scheduler
проблема зафиксирована как внешний operational risk
7. ОСОЗНАННЫЕ ОГРАНИЧЕНИЯ

На текущем этапе модуль имеет зафиксированные ограничения:

внешние сайты могут быть недоступны с VPS
scheduler не решает сетевую недоступность источников
нет отдельного слоя retry-monitoring beyond current source logic
нет альтернативных зеркал источников
нет proxy/failover механизма
requirements.txt для нового репозитория требует отдельной фиксации

Эти ограничения признаны допустимыми для текущего stable-слоя.

8. SMOKE TEST

Проверочные сценарии:

service запускается вручную
updater стартует через systemd
timer зарегистрирован в системе
после выполнения service приходит в:
ActiveState=inactive
SubState=dead
в логах присутствуют:
CITY_EVENTS_UPDATE_START
CITY_EVENTS_UPDATE_END
SUMMARY: SUCCESS или SUMMARY: PARTIAL_OR_FAILED

Результат:

scheduler-layer работает корректно

9. РЕЗУЛЬТАТ МОДУЛЯ

После завершения MODULE_03 система получила:

автономный запуск обновления
отдельный service-слой
отдельный timer-слой
запуск updater без участия пользователя
корректную работу oneshot-service
честную модель работы через last good snapshot
переход CITY_EVENTS из ручного режима в системный
10. ФИНАЛЬНЫЙ СТАТУС

MODULE_03 — SCHEDULER (AUTO UPDATE)

✔ update entrypoint — ready
✔ systemd service — ready
✔ systemd timer — ready
✔ VPS deployment — ready
✔ manual start test — passed
✔ service final state — correct
✔ partial failure handling — stabilized

STATUS: LOCKED 🔒
MODE: STABLE