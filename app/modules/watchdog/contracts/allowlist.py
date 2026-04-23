from __future__ import annotations

ALLOWED_ROUTER_MODULES: tuple[str, ...] = (
    "app.handlers.start",
    "app.modules.language.handlers",
    "app.modules.directory.router",
    "app.modules.city_events.ui.router",
    "app.modules.admin.handlers.admin_health",
    "app.modules.admin.handlers.admin_help",
)

ALLOWED_JSON_DIRS: tuple[str, ...] = (
    "app/data/public",
    "app/data/system/health",
    "app/data/objects",
)

FORBIDDEN_MODULE_PATTERNS: tuple[str, ...] = (
    "main",
    "test_",
    "app.modules.city_events.services.update_all",
    "app.modules.city_events.services.public_health_reader",
    "app.modules.directory.category_menu",
    "app.modules.directory.card_view",
)

