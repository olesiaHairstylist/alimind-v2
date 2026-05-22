from __future__ import annotations

import asyncio
from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

from app.core.text import get_text
from app.modules.core.language.service import get_user_lang

from app.modules.directory.contracts.callbacks import (
    parse_directory_open_cb,
)

from app.modules.directory.render.card_render import render_object_card
from app.modules.directory.render.keyboard_render import (
    build_directory_object_back_kb,
)

from app.modules.directory.services.loader import load_object_by_id
from app.modules.directory.services.media_resolver import (
    resolve_object_photo,
    resolve_object_video,
)

router = Router()

_user_locks: dict[int, asyncio.Lock] = {}


def _texts(lang: str) -> dict[str, str]:
    return {
        "ru": {
            "error": "Ошибка объекта",
            "empty": "Объект не найден",
        },
        "en": {
            "error": "Object error",
            "empty": "Object not found",
        },
        "tr": {
            "error": "Nesne hatası",
            "empty": "Nesne bulunamadı",
        },
    }.get(lang, {
        "error": "Ошибка объекта",
        "empty": "Объект не найден",
    })


def _to_buffered_file(path: Path) -> BufferedInputFile:
    """Читает файл в память и сразу отпускает файл на диске."""
    return BufferedInputFile(
        path.read_bytes(),
        filename=path.name,
    )


def _resolve_object_view(
    object_id: str,
    lang: str,
) -> tuple[dict, str, object, Path | None, Path | None] | None:
    obj = load_object_by_id(object_id)
    if not obj:
        return None

    print("OBJECT MAP DEBUG:", object_id, obj.get("lat"), obj.get("lng"))

    category_id = obj.get("category", "")
    subcategory_id = obj.get("subcategory", "")

    card_text = render_object_card(obj, lang=lang)
    reply_markup = build_directory_object_back_kb(
        category_id,
        subcategory_id,
        lang,
        object_id=object_id,
        has_maps=bool(obj.get("lat") and obj.get("lng")),
        instagram_url=get_text(obj.get("instagram"), lang),
    )

    image_path = resolve_object_photo(object_id)
    video_path = resolve_object_video(object_id)

    return obj, card_text, reply_markup, image_path, video_path


async def send_directory_object_card(message: Message, object_id: str, lang: str) -> bool:
    view = _resolve_object_view(object_id, lang)
    if not view:
        return False

    _, card_text, reply_markup, image_path, video_path = view

    if video_path:
        try:
            await message.answer_video(
                video=_to_buffered_file(video_path),
                caption=card_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        except (TelegramNetworkError, TelegramBadRequest, OSError):
            await message.answer(
                card_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

    elif image_path:
        await message.answer_photo(
            photo=_to_buffered_file(image_path),
            caption=card_text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    else:
        await message.answer(
            card_text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    return True


@router.callback_query(F.data.startswith("directory:open:"))
async def open_directory_object(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    lock = _user_locks.setdefault(user_id, asyncio.Lock())

    if lock.locked():
        await callback.answer()
        return

    async with lock:
        data = callback.data or ""
        object_id = parse_directory_open_cb(data)
        lang = get_user_lang(callback.from_user.id) or "ru"
        texts = _texts(lang)

        if not object_id:
            await callback.answer(texts["error"], show_alert=False)
            return

        view = _resolve_object_view(object_id, lang)

        if not view:
            await callback.answer(texts["empty"], show_alert=False)
            return

        await callback.answer()

        _, card_text, reply_markup, image_path, video_path = view

        print("VIDEO PATH:", video_path)
        print("VIDEO EXISTS:", bool(video_path))

        if video_path:
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            try:
                await callback.message.answer_video(
                    video=_to_buffered_file(video_path),
                    caption=card_text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            except (TelegramNetworkError, TelegramBadRequest, OSError):
                await callback.message.answer(
                    card_text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )

        elif image_path:
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            await callback.message.answer_photo(
                photo=_to_buffered_file(image_path),
                caption=card_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

        elif callback.message.photo or callback.message.video:
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            await callback.message.answer(
                card_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

        else:
            await callback.message.edit_text(
                card_text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )