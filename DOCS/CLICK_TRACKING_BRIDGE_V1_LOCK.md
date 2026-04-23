DOCUMENT: CLICK_TRACKING_BRIDGE_V1_LOCK

PROJECT: ALIMIND_V2
MODULE: TICKETS / PARTNERS
STATUS: LOCKED
DATE: 2026-04-14

1. PURPOSE

Внедрить минимальный безопасный механизм отслеживания взаимодействия пользователя с партнёрскими предложениями в tickets flow.

Система должна:

фиксировать факт клика
не влиять на ранжирование
не изменять логику выбора
не ломать UX
не вводить аналитику и хранение данных
2. PROBLEM (BEFORE)

До внедрения:

партнёрские ссылки отображались как plain text URL
Telegram не генерировал callback на нажатие
система не видела клики
отсутствовал любой feedback signal

Фактически:

user → click → переход
system → blind
3. SOLUTION

Введён CLICK TRACKING BRIDGE

Изменение interaction surface:

Было:
текст + URL (неотслеживаемый)
Стало:
inline button → callback → лог → выдача URL
4. FINAL USER FLOW
user
→ /tickets_preview
→ видит partner block
→ нажимает кнопку партнёра
→ callback срабатывает
→ система логирует клик
→ бот отправляет follow-up с реальной ссылкой
→ пользователь переходит
5. CLICK EVENT FORMAT

Минимальный лог:

[CLICK] partner=<partner_id> user_id=<user_id> source=tickets_preview
6. IMPLEMENTATION DETAILS
6.1 Interaction Layer
raw URL удалён из preview-текста
основной путь взаимодействия — inline кнопка
6.2 Callback Contract

Используется:

partner:tickets_preview:click:<partner_id>

Контракт не изменён, только задействован.

6.3 Handler

Локация:

app/modules/partners/handlers/tickets_preview_click.py

Функции:

парсинг partner_id
логирование события
отправка follow-up сообщения с URL
6.4 Delivery Model

После клика:

бот → отправляет сообщение с URL

Без popup-спама
Без дополнительных UX-слоёв

7. WHAT WAS NOT CHANGED

Строго сохранены:

ranking logic
selection logic
compute_scores_for_offers(...)
apply_engagement_scoring(...)
engagement_weight_control.py
engagement_quality_gates.py
engagement_token_boost.py
engagement_monetization.py
explainability
audit trace
operator debug
storage schema
loader
object ids
callback contracts (не изменены, только использованы)
8. INVARIANTS

После внедрения:

tickets flow остаётся стабильным
partner block отображается
UI не деградирует
система не зависит от клика
click tracking не влияет на выдачу
handler fail-safe (не ломает поток)
9. LIMITATIONS (KNOWN & ACCEPTED)
Telegram Constraint

Невозможно:

один клик = callback + открытие URL

Поэтому используется мост:

click → callback → лог → выдача ссылки
Tracking Scope

Система фиксирует:

👉 факт взаимодействия (intent)

Система НЕ фиксирует:

фактический переход
время на сайте
конверсии
10. VERIFICATION RESULT

Подтверждено:

кнопки отображаются
callback работает
follow-up сообщение приходит
runtime не падает
smoke test passed
compileall passed
11. SYSTEM STATE AFTER LOCK

Система перешла из состояния:

blind output

в состояние:

observable interaction
12. NEXT POSSIBLE LAYERS (NOT IMPLEMENTED)

НЕ входят в текущий scope:

CTR aggregation
persistent storage
re-ranking по кликам
quality filtering
token-based weighting
outbound redirect tracking
analytics layer
13. FINAL STATUS
CLICK_TRACKING_BRIDGE_V1 = LOCKED
14. STRATEGIC NOTE

Это первый слой, который даёт системе:

👉 видеть поведение пользователя

Без этого невозможны:

адаптация
оптимизация
справедливое ранжирование
экономическая модель