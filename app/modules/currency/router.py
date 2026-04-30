from aiogram import Router

from .handlers import handlers  # если есть пакет
# или импортируете конкретные файлы

router = Router()

# пример:
# router.include_router(menu_router)
# router.include_router(convert_router)