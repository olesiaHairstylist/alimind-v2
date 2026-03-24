from pathlib import Path
from app.modules.city_events.sources.asat_water_adapter import run_and_save

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "app" / "data" / "city_events"

path = run_and_save(DATA_DIR)

print("SAVED:", path)
print("ABSOLUTE:", path.resolve())
print("EXISTS:", path.exists())