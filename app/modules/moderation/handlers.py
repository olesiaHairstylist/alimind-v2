from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


def clear_status(text: str) -> str:
    return (
        text
        .replace("✅ APPROVED\n\n", "")
        .replace("❌ REJECTED\n\n", "")
        .replace("⏳ SAVED FOR LATER\n\n", "")
    )


@router.callback_query(F.data == "mod:approve")
async def moderation_approve(callback: CallbackQuery):
    await callback.answer("Approved")

    old_text = callback.message.text or ""
    clean_text = clear_status(old_text)

    await callback.message.edit_text(
        "✅ APPROVED\n\n" + clean_text
    )


@router.callback_query(F.data == "mod:reject")
async def moderation_reject(callback: CallbackQuery):
    await callback.answer("Rejected")

    old_text = callback.message.text or ""
    clean_text = clear_status(old_text)

    await callback.message.edit_text(
        "❌ REJECTED\n\n" + clean_text
    )


@router.callback_query(F.data == "mod:later")
async def moderation_later(callback: CallbackQuery):
    await callback.answer("Saved for later")

    old_text = callback.message.text or ""
    clean_text = clear_status(old_text)

    await callback.message.edit_text(
        "⏳ SAVED FOR LATER\n\n" + clean_text
    )