from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]  # до app/

DATA_DIR = BASE_DIR / "data" / "city_events"

DUTY_PHARMACIES_FILE = DATA_DIR / "duty_pharmacies.json"
EMERGENCY_CONTACTS_FILE = DATA_DIR / "emergency_contacts.json"