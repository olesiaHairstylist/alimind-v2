AB_TEST_WEIGHT_V1 LOCKED

Дата фиксации: 2026-04-13

Статус:
LOCKED · SAFE · ISOLATED

Суть:
В partners module внедрён A/B test layer для engagement weight без изменения tickets logic, handlers, storage schema и selection logic.

Файлы:
- app/modules/partners/services/ab_test.py
- app/modules/partners/services/engagement_scoring.py

Что зафиксировано:
1. Пользователь детерминированно попадает в группу A/B через:
   sum(ord(ch) for ch in user_key) % 2
2. Группа A получает engagement_weight = 0.0
3. Группа B получает engagement_weight = 0.5
4. Engagement scoring добавляет в offer:
   - ab_group
   - engagement_click_count
   - engagement_score
   - engagement_weight
   - weighted_engagement_score
   - final_partner_score
5. Для пустого user_key added early return:
   if not normalized_user_key: return offers
   Это исключает загрязнение engagement memory и A/B эксперимента через пустые ключи.
6. Sorting logic unchanged
7. Scoring formula unchanged кроме weight layer
8. Tickets smoke test passed after patch
9. No rendering regression observed
10. No other system layers modified

Инварианты:
- tickets untouched
- handlers untouched
- storage untouched
- selection untouched
- empty user_key must always bypass engagement scoring
- A/B logic must stay deterministic
- current sorting must remain unchanged

Текущее состояние:
A/B тестовый слой готов к сбору impressions/click metrics.
Следующий логичный модуль:
ENGAGEMENT_DECAY_V1
ENGAGEMENT_DECAY_V1 LOCKED

Дата фиксации: 2026-04-13

Статус:
LOCKED · SAFE · ISOLATED · TIME-AWARE

Суть:
В partners engagement scoring внедрён time-decay layer, который ослабляет влияние старых кликов на partner ranking без изменения A/B logic, storage schema, selection, sorting, tickets logic или handlers.

Файл:
- app/modules/partners/services/engagement_scoring.py

Что зафиксировано:
1. Добавлен локальный datetime parsing helper:
   _parse_iso_datetime(value)
2. Добавлен decay helper:
   _get_decay_multiplier(last_clicked_at)
3. Decay table:
   - 0–3 days => 1.0
   - 4–14 days => 0.7
   - 15–30 days => 0.4
   - 31+ days => 0.1
4. Raw engagement score model preserved:
   0=0, 1=10, 2=20, 3=30, 4+=40
5. Formula order fixed as:
   raw engagement score
   -> decayed engagement score
   -> weighted engagement score via A/B weight
   -> final partner score
6. Added output fields:
   - engagement_last_clicked_at
   - engagement_decay_multiplier
   - decayed_engagement_score
7. Existing fields preserved:
   - ab_group
   - engagement_click_count
   - engagement_score
   - engagement_weight
   - weighted_engagement_score
   - final_partner_score
8. Empty user_key early return preserved
9. A/B logic unchanged
10. Sorting unchanged
11. Selection logic unchanged
12. Tickets files untouched
13. Handlers untouched
14. Storage schema untouched
15. Smoke test passed with no rendering regression

Инварианты:
- empty user_key must always bypass engagement scoring
- raw engagement score model must stay unchanged
- decay must be applied before A/B weight
- A/B logic must remain deterministic
- sorting must remain unchanged
- selection must remain unchanged
- tickets / handlers / storage must remain untouched

Текущее состояние:
Engagement layer is now time-aware and ready for cleaner behavioral ranking.

Следующий логичный модуль:
ENGAGEMENT_IMPRESSIONS_V1
или
ENGAGEMENT_ANALYTICS_V1