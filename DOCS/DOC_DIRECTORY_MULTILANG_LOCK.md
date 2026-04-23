ALIMIND — DIRECTORY MULTILANG SYSTEM

Дата: 2026-04-07
Статус: ✅ DONE · STABLE · LOCKED

🧠 Цель этапа

Перевести модуль Directory (Услуги) на полноценную мультиязычную систему без поломки архитектуры и без потери обратной совместимости.

⚙️ Что было сделано
1. Ввод мультиязычных данных (FSM)

Файл:

app/modules/directory/handlers/partner_add.py

Реализовано:

последовательный ввод: ru → en → tr
поддержка "-" → копирование RU
все поля теперь словари:
"title": { "ru": "...", "en": "...", "tr": "..." }

Поля:

title
description_short
description_full
location
contact
2. Единый текстовый слой

Создан файл:

app/core/text.py
def get_text(value, lang="ru"):
    if isinstance(value, dict):
        return value.get(lang) or value.get("ru") or ""
    return value or ""

Назначение:

единый доступ к тексту
поддержка старых и новых данных
fallback: lang → ru → ""
3. Обновление render слоя

Файл:

app/modules/directory/render/card_render.py

Изменения:

все текстовые поля проходят через get_text
удалён локальный resolver (localized_value.py)

Результат:

карточки работают с:
старыми строками
новыми dict
4. Локализация UI (категории / подкатегории)

Файл:

app/modules/directory/contracts/categories.py

Добавлено:

SUBCATEGORY_TITLES_I18N

Созданы функции:

get_category_title(...)
get_subcategory_title(...)
5. Исправлен баг UI

Проблема:

document_translation

показывался как текст кнопки

Решение:

внедрён слой получения названия
UI теперь показывает:
🌐 Перевод документов
🌐 Document Translation
🌐 Belge Çevirisi
6. Handler подкатегории обновлён

Файл:

app/modules/directory/handlers/subcategory.py

Изменения:

добавлен get_subcategory_title
заголовок экрана теперь локализован
🧪 Проверка

Пройдено:

Карточки
RU / EN / TR отображаются корректно
fallback работает
Подкатегории
больше нет raw id
текст локализован
Callback
не изменён:
directory:subcategory:legal:document_translation
Старые объекты
работают без изменений
🚫 Что НЕ трогали
loader.py
partner_saver.py
callback contracts
FSM логика (кроме ввода текста)
JSON структура (на уровне сохранения)
city_events
WordPress API
routing
📊 Итоговая архитектура
DATA (json)
   ↓
get_text (core)
   ↓
render (card / UI)
   ↓
user interface
🧠 Ключевой результат

Создан единый текстовый слой системы, который:

поддерживает старые данные
поддерживает мультиязычность
не ломает архитектуру
масштабируется