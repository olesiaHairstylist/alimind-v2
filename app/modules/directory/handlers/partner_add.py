from __future__ import annotations

import os
import json
from pathlib import Path
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.modules.directory.services.photo_service import save_object_photo


from app.modules.directory.contracts.categories import (
    CATEGORY_ORDER,
    CATEGORY_SUBCATEGORY_ORDER,
    CATEGORY_TITLES,
    SUBCATEGORY_TITLES,
)
from app.modules.directory.render.card_render import render_object_card
from app.modules.directory.services.partner_saver import (
    build_partner_payload,
    save_partner,
    generate_id,
)

router = Router()
OBJECTS_PATH = Path("app/data/objects")


def save_object_by_id(object_id: str, obj: dict) -> bool:
    file_path = OBJECTS_PATH / f"{object_id}.json"

    if not file_path.exists():
        return False

    file_path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return True


FSM_CATEGORY_PREFIX = "fsm:cat:"
FSM_SUBCATEGORY_PREFIX = "fsm:sub:"
FSM_CONFIRM_SAVE = "fsm:confirm:save"
FSM_CONFIRM_CANCEL = "fsm:confirm:cancel"

ML_LANG_ORDER = ("ru", "en", "tr")
ML_FIELD_LABELS = {
    "title": "название партнера",
    "description_short": "краткое описание",
    "description_full": "полное описание",
    "location": "локацию",
    "contact": "контакт",
}


def _build_ml_prompt(field: str, lang: str) -> str:
    field_label = ML_FIELD_LABELS.get(field, field)

    if lang == "ru":
        return f"Введите {field_label} (RU):"

    return f"Введите {field_label} ({lang.upper()}) или '-' чтобы взять RU:"


def _next_ml_lang(value: dict[str, str]) -> str | None:
    for lang in ML_LANG_ORDER:
        if lang not in value:
            return lang
    return None


def _apply_ml_value(value: dict[str, str], lang: str, text: str) -> tuple[dict[str, str] | None, str | None]:
    if not text:
        return None, "Пустое значение. Введите текст."

    if lang == "ru":
        if text == "-":
            return None, "Для RU нельзя использовать '-'. Введите текст."
        return {**value, "ru": text}, None

    ru_value = value.get("ru", "").strip()
    if text == "-":
        if not ru_value:
            return None, "RU значение не найдено. Сначала заполните RU."
        text = ru_value

    return {**value, lang: text}, None


async def _collect_ml_field_step(message: Message, state: FSMContext, field: str) -> tuple[bool, dict[str, str] | None]:
    data = await state.get_data()
    current_raw = data.get(field)
    current: dict[str, str] = current_raw if isinstance(current_raw, dict) else {}

    lang = _next_ml_lang(current)
    if not lang:
        return True, current

    text = (message.text or "").strip()
    updated, error = _apply_ml_value(current, lang, text)

    if error or not updated:
        await message.answer(error or _build_ml_prompt(field, lang))
        return False, None

    await state.update_data(**{field: updated})

    next_lang = _next_ml_lang(updated)
    if next_lang:
        await message.answer(_build_ml_prompt(field, next_lang))
        return False, None

    return True, updated


def _build_payload_preview(obj: dict) -> str:
    return "Проверьте итоговую структуру JSON:\n\n" + json.dumps(obj, ensure_ascii=False, indent=2)


class PartnerAddStates(StatesGroup):
    waiting_id = State()
    waiting_title = State()
    waiting_category = State()
    waiting_subcategory = State()
    waiting_description_short = State()
    waiting_description_full = State()
    waiting_location = State()
    waiting_contact = State()
    waiting_photo = State()
    waiting_confirm = State()


class PartnerCheckStates(StatesGroup):
    waiting_id = State()


class PartnerDisableStates(StatesGroup):
    waiting_id = State()

class PartnerUpdateStates(StatesGroup):
    waiting_id = State()
    waiting_description_short = State()

class PartnerPhotoStates(StatesGroup):
    waiting_id = State()
    waiting_photo = State()


@router.message(Command("partner_check"))
async def partner_check_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PartnerCheckStates.waiting_id)
    await message.answer("Введите ID партнёра:")
from app.modules.directory.services.loader import load_object_by_id

@router.message(PartnerCheckStates.waiting_id)
async def partner_check_id(message: Message, state: FSMContext) -> None:
    partner_id = (message.text or "").strip()

    if not partner_id:
        await message.answer("ID пустой. Введите ID:")
        return

    obj = load_object_by_id(partner_id)

    if not obj:
        await message.answer("❌ Партнёр не найден")
    else:
        await message.answer("✅ Партнёр найден:\n")
        await message.answer(render_object_card(obj))

    await state.clear()
@router.message(Command("partner_disable"))
async def partner_disable_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PartnerDisableStates.waiting_id)
    await message.answer("Введите ID партнёра для отключения:")

@router.message(PartnerDisableStates.waiting_id)
async def partner_disable_apply(message: Message, state: FSMContext) -> None:
    partner_id = (message.text or "").strip()

    if not partner_id:
        await message.answer("ID пустой. Введите ID:")
        return

    obj = load_object_by_id(partner_id)

    if not obj:
        await message.answer("❌ Партнёр не найден")
        await state.clear()
        return

    obj["is_partner"] = False

    result = save_partner(obj)

    if not result["ok"]:
        await message.answer(
            f"❌ Ошибка отключения партнёра\n\n"
            f"Ошибка: {result.get('error', '—')}"
        )
        await state.clear()
        return

    await message.answer(
        f"✅ Партнёр отключён и синхронизирован\n\n"
        f"ID: {partner_id}"
    )
    await state.clear()

@router.message(Command("partner_update"))
async def partner_update_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PartnerUpdateStates.waiting_id)
    await message.answer("Введите ID партнёра для обновления:")

@router.message(PartnerUpdateStates.waiting_id)
async def partner_update_id(message: Message, state: FSMContext) -> None:
    partner_id = (message.text or "").strip()

    if not partner_id:
        await message.answer("ID пустой. Введите ID:")
        return

    obj = load_object_by_id(partner_id)

    if not obj:
        await message.answer("❌ Партнёр не найден")
        await state.clear()
        return

    await state.update_data(partner_id=partner_id)

    await message.answer("✅ Партнёр найден. Текущая карточка:")
    await message.answer(render_object_card(obj))

    current_value = obj.get("description_short", "")
    await state.set_state(PartnerUpdateStates.waiting_description_short)
    await message.answer(
        "Введите новое краткое описание (description_short):\n\n"
        f"Сейчас: {current_value}"
    )

@router.message(PartnerUpdateStates.waiting_description_short)
async def partner_update_description_short(message: Message, state: FSMContext) -> None:
    new_value = (message.text or "").strip()

    if not new_value:
        await message.answer("Краткое описание не должно быть пустым. Введите новое значение:")
        return

    data = await state.get_data()
    partner_id = data.get("partner_id")

    if not partner_id:
        await message.answer("❌ Ошибка состояния. ID не найден.")
        await state.clear()
        return

    obj = load_object_by_id(partner_id)

    if not obj:
        await message.answer("❌ Партнёр не найден при сохранении")
        await state.clear()
        return

    obj["description_short"] = new_value

    result = save_partner(obj)

    if not result["ok"]:
        await message.answer(
            f"❌ Ошибка обновления\n\n"
            f"Ошибка: {result.get('error', '—')}"
        )
        await state.clear()
        return

    await message.answer(
        "✅ Краткое описание обновлено и синхронизировано с WordPress\n\n"
        f"ID: {partner_id}\n"
        f"description_short: {new_value}\n"
        f"HTTP: {result['api'].get('status', '—')}"
    )
    await message.answer("Обновлённая карточка:")
    await message.answer(render_object_card(obj))

    await state.clear()
def build_categories_kb():
    kb = InlineKeyboardBuilder()

    for category_id in CATEGORY_ORDER:
        title = CATEGORY_TITLES.get(category_id, category_id)
        kb.button(text=title, callback_data=f"{FSM_CATEGORY_PREFIX}{category_id}")

    kb.adjust(2)
    return kb.as_markup()

@router.message(PartnerAddStates.waiting_description_short)
async def add_partner_description_short(message: Message, state: FSMContext) -> None:
    completed, _ = await _collect_ml_field_step(message, state, "description_short")
    if not completed:
        return

    await state.set_state(PartnerAddStates.waiting_description_full)
    await message.answer(_build_ml_prompt("description_full", "ru"))

def build_subcategories_kb(category_id: str):
    kb = InlineKeyboardBuilder()

    sub_ids = CATEGORY_SUBCATEGORY_ORDER.get(category_id, [])
    for subcategory_id in sub_ids:
        title = SUBCATEGORY_TITLES.get(subcategory_id, subcategory_id)
        kb.button(text=title, callback_data=f"{FSM_SUBCATEGORY_PREFIX}{subcategory_id}")

    kb.adjust(2)
    return kb.as_markup()


def build_partner_confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Сохранить", callback_data=FSM_CONFIRM_SAVE)
    kb.button(text="❌ Отмена", callback_data=FSM_CONFIRM_CANCEL)
    kb.adjust(2)
    return kb.as_markup()


def parse_category_callback(data: str | None) -> str | None:
    if not data or not data.startswith(FSM_CATEGORY_PREFIX):
        return None
    return data.removeprefix(FSM_CATEGORY_PREFIX).strip() or None


def parse_subcategory_callback(data: str | None) -> str | None:
    if not data or not data.startswith(FSM_SUBCATEGORY_PREFIX):
        return None
    return data.removeprefix(FSM_SUBCATEGORY_PREFIX).strip() or None


@router.message(Command("add_partner"))
async def add_partner_start(message: Message, state: FSMContext) -> None:
    admin_id_raw = os.getenv("ADMIN_ID")

    if not admin_id_raw or not admin_id_raw.isdigit():
        await message.answer("ADMIN_ID не настроен.")
        return

    admin_id = int(admin_id_raw)

    if not message.from_user or message.from_user.id != admin_id:
        await message.answer("Нет доступа.")
        return

    await state.clear()
    await state.set_state(PartnerAddStates.waiting_title)
    await message.answer(_build_ml_prompt("title", "ru"))


@router.message(PartnerAddStates.waiting_title)
async def add_partner_title(message: Message, state: FSMContext) -> None:
    completed, title_value = await _collect_ml_field_step(message, state, "title")
    if not completed or not title_value:
        return

    title_ru = title_value.get("ru", "").strip()
    data = await state.get_data()

    update_data: dict[str, object] = {"title": title_value}

    if not data.get("id"):
        update_data["id"] = generate_id(title_ru)

    await state.update_data(**update_data)
    await state.set_state(PartnerAddStates.waiting_category)
    await message.answer(
        "Выберите категорию:",
        reply_markup=build_categories_kb(),
    )


@router.callback_query(
    PartnerAddStates.waiting_category,
    F.data.startswith(FSM_CATEGORY_PREFIX),
)
async def add_partner_category(callback: CallbackQuery, state: FSMContext) -> None:
    category_id = parse_category_callback(callback.data)

    if not category_id:
        await callback.answer("Ошибка категории", show_alert=False)
        return

    await state.update_data(category=category_id)
    await state.set_state(PartnerAddStates.waiting_subcategory)

    await callback.message.edit_text(
        "Выберите подкатегорию:",
        reply_markup=build_subcategories_kb(category_id),
    )
    await callback.answer()


@router.callback_query(
    PartnerAddStates.waiting_subcategory,
    F.data.startswith(FSM_SUBCATEGORY_PREFIX),
)
async def add_partner_subcategory(callback: CallbackQuery, state: FSMContext) -> None:
    subcategory_id = parse_subcategory_callback(callback.data)

    if not subcategory_id:
        await callback.answer("Ошибка подкатегории", show_alert=False)
        return

    await state.update_data(subcategory=subcategory_id)
    await state.set_state(PartnerAddStates.waiting_description_short)

    await callback.message.edit_text(_build_ml_prompt("description_short", "ru"))
    await callback.answer()


@router.message(PartnerUpdateStates.waiting_description_short)
async def partner_update_description_short(message: Message, state: FSMContext) -> None:
    new_value = (message.text or "").strip()

    if not new_value:
        await message.answer("Краткое описание не должно быть пустым. Введите новое значение:")
        return

    data = await state.get_data()
    partner_id = data.get("partner_id")

    if not partner_id:
        await message.answer("❌ Ошибка состояния. ID не найден.")
        await state.clear()
        return

    obj = load_object_by_id(partner_id)

    if not obj:
        await message.answer("❌ Партнёр не найден при сохранении")
        await state.clear()
        return

    obj["description_short"] = new_value

    result = save_partner(obj)

    if not result["ok"]:
        await message.answer(
            f"❌ Ошибка обновления\n\n"
            f"Ошибка: {result.get('error', '—')}\n"
            f"Ответ: {result.get('response', '—')}"
        )
        await state.clear()
        return

    await message.answer(
        "✅ Краткое описание обновлено и синхронизировано с WordPress\n\n"
        f"ID: {partner_id}\n"
        f"description_short: {new_value}\n"
        f"HTTP: {result['api'].get('status', '—')}"
    )
    await message.answer("Обновлённая карточка:")
    await message.answer(render_object_card(obj))

    await state.clear()


@router.message(PartnerAddStates.waiting_description_full)
async def add_partner_description_full(message: Message, state: FSMContext) -> None:
    completed, _ = await _collect_ml_field_step(message, state, "description_full")
    if not completed:
        return

    await state.set_state(PartnerAddStates.waiting_location)
    await message.answer(_build_ml_prompt("location", "ru"))


@router.message(PartnerAddStates.waiting_location)
async def add_partner_location(message: Message, state: FSMContext) -> None:
    completed, _ = await _collect_ml_field_step(message, state, "location")
    if not completed:
        return

    await state.set_state(PartnerAddStates.waiting_contact)
    await message.answer(_build_ml_prompt("contact", "ru"))


@router.message(PartnerAddStates.waiting_contact)
async def add_partner_contact(message: Message, state: FSMContext) -> None:
    completed, _ = await _collect_ml_field_step(message, state, "contact")
    if not completed:
        return

    await state.set_state(PartnerAddStates.waiting_photo)
    await message.answer("Отправьте фото или напишите /skip")

@router.callback_query(
    PartnerAddStates.waiting_confirm,
    F.data == FSM_CONFIRM_SAVE,
)
async def add_partner_confirm_save(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    obj = build_partner_payload(data)

    result = save_partner(obj)

    await state.clear()

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if result["ok"]:
        await callback.message.answer(
            f"✅ Партнёр сохранён и отправлен в WordPress\n\n"
            f"ID: {obj['id']}\n"
            f"Файл: {result['path']}\n"
            f"HTTP: {result['api'].get('status', '—')}\n"
            f"Ответ API: {result['api'].get('response', '—')}"
        )
    else:
        await callback.message.answer(
            f"❌ Ошибка отправки в WordPress\n\n"
            f"Этап: {result.get('stage', '—')}\n"
            f"HTTP: {result.get('status', '—')}\n"
            f"Ошибка: {result.get('error', '—')}\n"
            f"Ответ: {result.get('response', '—')}"
        )

    await callback.answer()

@router.message(PartnerAddStates.waiting_photo, F.photo)
async def add_partner_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    object_id = data.get("id")

    image_path = await save_object_photo(message, object_id, message.bot)

    await state.update_data(image_path=image_path)

    data = await state.get_data()
    obj = build_partner_payload(data)

    await state.set_state(PartnerAddStates.waiting_confirm)

    await message.answer(_build_payload_preview(obj))
    await message.answer("Проверьте карточку:")
    await message.answer(
        render_object_card(obj),
        reply_markup=build_partner_confirm_kb(),
    )

@router.message(PartnerAddStates.waiting_photo, Command("skip"))
async def skip_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    obj = build_partner_payload(data)

    await state.set_state(PartnerAddStates.waiting_confirm)

    await message.answer(_build_payload_preview(obj))
    await message.answer("Проверьте карточку:")
    await message.answer(
        render_object_card(obj),
        reply_markup=build_partner_confirm_kb(),
    )

@router.callback_query(
    PartnerAddStates.waiting_confirm,
    F.data == FSM_CONFIRM_CANCEL,
)
async def add_partner_confirm_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer("❌ Добавление партнёра отменено.")
    await callback.answer()
@router.message(Command("partner_photo"))
async def partner_photo_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(PartnerPhotoStates.waiting_id)
    await message.answer("Введите ID партнёра:")


@router.message(PartnerPhotoStates.waiting_id)
async def partner_photo_get_id(message: Message, state: FSMContext):
    obj = load_object_by_id(message.text.strip())

    if not obj:
        await message.answer("❌ Не найден")
        return

    await state.update_data(object_id=obj["id"])
    await state.set_state(PartnerPhotoStates.waiting_photo)
    await message.answer("Отправьте фото")


@router.message(PartnerPhotoStates.waiting_photo, F.photo)
async def partner_photo_save(message: Message, state: FSMContext):
    data = await state.get_data()
    object_id = data.get("object_id")

    if not object_id:
        await message.answer("❌ Не найден ID объекта")
        await state.clear()
        return

    path = await save_object_photo(message, object_id, message.bot)

    obj = load_object_by_id(object_id)
    if not obj:
        await message.answer("❌ Объект не найден")
        await state.clear()
        return

    obj["image_path"] = path
    result = save_partner(obj)

    if result.get("ok"):
        await message.answer("✅ Фото добавлено")
    else:
        await message.answer("✅ Фото добавлено локально, но WordPress не обновился")

    await state.clear()