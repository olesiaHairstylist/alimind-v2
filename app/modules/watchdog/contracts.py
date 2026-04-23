from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
SYSTEM_DIR = BASE_DIR / "app" / "data" / "system"
PUBLIC_CITY_EVENTS_DIR = BASE_DIR / "app" / "data" / "public" / "city_events"

SNAPSHOT_PATH = SYSTEM_DIR / "watchdog_snapshot.json"
LOG_PATH = SYSTEM_DIR / "watchdog.log"
STATE_PATH = SYSTEM_DIR / "watchdog_state.json"

ALLOWED_STATUSES: tuple[str, ...] = ("ok", "empty", "error")
ALERT_COOLDOWN_SECONDS = 30 * 60

CITY_EVENT_FILES: dict[str, str] = {
    "electricity": "electricity_outages_today.json",
    "water": "water_outages_today.json",
    "pharmacies": "duty_pharmacies_today.json",
    "emergency": "emergency_contacts.json",
}

EXPECTED_EMPTY: dict[str, bool] = {
    "electricity": True,
    "water": True,
    "pharmacies": False,
    "emergency": False,
}

MODULE_LABELS: dict[str, str] = {
    "electricity": "Электричество",
    "water": "Вода",
    "pharmacies": "Дежурные аптеки",
    "emergency": "Экстренные контакты",
    "watchdog": "Watchdog",
}

GROUPED_STALE_WARNING_KEY = "grouped_stale_warning"
