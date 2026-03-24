MODULE_03_STEP_1 — DATA STRUCTURE (JSON карточки)
1. Где храним
app/data/objects/

На старте — 1 файл = 1 карточка.
Это проще для контроля и ревизии.

Пример:

app/data/objects/
 ├ beauty_olesya_001.json
 ├ transfer_alanya_001.json
 ├ translator_ru_tr_001.json
2. Единый стандарт карточки
{
  "id": "beauty_olesya_001",
  "status": "active",
  "is_partner": true,
  "category": "beauty",
  "subcategory": "hair",
  "name": "Olesya Hairstylist",
  "title": "Женский парикмахер в Алании",
  "short_description": "Стрижки, окрашивание, уход за волосами.",
  "services": [
    "Женская стрижка",
    "Окрашивание",
    "Укладка"
  ],
  "location": "Alanya",
  "district": "Mahmutlar",
  "address": "",
  "phone": "",
  "telegram": "",
  "whatsapp": "",
  "instagram": "@olesya.hair07",
  "site_url": "",
  "image": "https://site.com/media/olesya.jpg",
  "request_enabled": true,
  "partner_chat_id": "123456789",
  "bot_text": "Женский парикмахер. Стрижки, окрашивание, уход за волосами.",
  "site_text": "Партнёр AliMind. Женский парикмахер в Алании. Стрижки, окрашивание, уход за волосами.",
  "lang": [
    "ru"
  ],
  "updated_at": "2026-03-20",
  "sort_order": 100
}
3. Обязательные поля

Без них карточка невалидна:

id
status
is_partner
category
name
title
short_description
services
location
image
request_enabled
updated_at
sort_order
4. Условно-обязательные поля
Если request_enabled = true, обязательно:
partner_chat_id
Должен быть хотя бы один живой контакт:
phone
telegram
whatsapp
instagram
site_url
5. Разрешённые значения
status
active
inactive
is_partner
true
category

На старте:

beauty
transport
translation
home_services
sport
tourism
real_estate
health
daily
auto_services
6. Правила полей
id

уникальный

латиница

нижний регистр

без пробелов

Пример:

beauty_olesya_001
name

Короткое имя/бренд.

title

Человеческий заголовок для сайта и бота.

short_description

1–2 предложения, без рекламы и крика.

services

Список конкретных услуг, не пустой.

image

Одна главная картинка по URL.

sort_order

Число для сортировки внутри категории.

7. Что не добавляем в baseline

Пока запрещено:

reviews
rating
gallery
video
seo
badge
top
recommended
working_hours
coordinates
price_from
8. Первый минимальный рабочий объект

Вот ещё более короткий стартовый вариант:

{
  "id": "beauty_olesya_001",
  "status": "active",
  "is_partner": true,
  "category": "beauty",
  "subcategory": "hair",
  "name": "Olesya Hairstylist",
  "title": "Женский парикмахер в Алании",
  "short_description": "Стрижки, окрашивание, уход за волосами.",
  "services": [
    "Женская стрижка",
    "Окрашивание"
  ],
  "location": "Alanya",
  "district": "Mahmutlar",
  "address": "",
  "phone": "",
  "telegram": "",
  "whatsapp": "",
  "instagram": "@olesya.hair07",
  "site_url": "",
  "image": "https://site.com/media/olesya.jpg",
  "request_enabled": true,
  "partner_chat_id": "123456789",
  "bot_text": "Женский парикмахер в Алании.",
  "site_text": "Партнёр AliMind. Женский парикмахер в Алании.",
  "lang": ["ru"],
  "updated_at": "2026-03-20",
  "sort_order": 100
}
9. Инварианты step 1
1. 1 файл = 1 карточка
2. все карточки лежат только в app/data/objects/
3. все карточки = партнёры
4. единый формат для сайта и бота
5. фото хранится как URL
6. карточки не зашиваются в код