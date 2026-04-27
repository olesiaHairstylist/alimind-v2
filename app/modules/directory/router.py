from __future__ import annotations

from aiogram import Router

from app.modules.directory.handlers.menu import router as menu_router
from app.modules.directory.handlers.category import router as category_router
from app.modules.directory.handlers.object import router as object_router
from app.modules.directory.handlers.subcategory import router as subcategory_router
from app.modules.directory.handlers.partner_add import router as partner_add_router
from app.modules.directory.handlers.search import router as search_router

router = Router()
router.include_router(menu_router)
router.include_router(category_router)
router.include_router(subcategory_router)
router.include_router(object_router)
router.include_router(partner_add_router)
router.include_router(search_router)