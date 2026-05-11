from aiogram import Router

from app.modules.group_moderation.handlers import router as handlers_router

router = Router(name="group_moderation")
router.include_router(handlers_router)