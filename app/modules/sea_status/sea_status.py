from __future__ import annotations
import httpx
from datetime import datetime

MARINE_URL = (
    "https://marine-api.open-meteo.com/v1/marine"
    "?latitude=36.54&longitude=32.00"
    "&current=wave_height,sea_surface_temperature"
    "&timezone=auto&cell_selection=sea"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=36.54&longitude=32.00"
    "&current=wind_speed_10m,wind_direction_10m"
    "&timezone=auto"
)


def get_sea_status() -> dict:
    try:
        marine = httpx.get(MARINE_URL, timeout=8).json()
        weather = httpx.get(WEATHER_URL, timeout=8).json()

        current_marine = marine.get("current") or {}
        current_weather = weather.get("current") or {}

        temp = current_marine.get("sea_surface_temperature")
        waves = current_marine.get("wave_height")
        wind = current_weather.get("wind_speed_10m")

        if temp is None or waves is None:
            return {"ok": False, "error": "no_data"}

        temp = round(temp, 1)
        waves = round(waves, 1)
        wind = round(wind, 1) if wind is not None else None

        if waves <= 0.5 and temp >= 20 and (wind is None or wind <= 5):
            verdict = "excellent"
        elif waves <= 1.0 and temp >= 18:
            verdict = "normal"
        else:
            verdict = "bad"

        return {
            "ok": True,
            "temp": temp,
            "waves": waves,
            "wind": wind,
            "verdict": verdict,
            "updated": datetime.now().strftime("%H:%M"),
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}