from __future__ import annotations
from app.modules.city_events.sources.pharmacies_source import run_fetch as run_pharmacies_source
from app.modules.city_events.sources.water_source import run_fetch as run_water_source
from app.modules.city_events.services.water_public_builder import run_build as build_water_public
from app.modules.city_events.services.pharmacies_public_builder import build_public_from_raw as build_pharmacies_public
from app.modules.city_events.services.emergency_public_builder import build_public_from_raw as build_emergency_public


def update_electricity() -> None:
    from app.modules.city_events.sources.electricity_source import run_fetch as run_electricity_source
    from app.modules.city_events.services.electricity_public_builder import (

        build_public_from_raw as build_electricity_public,
    )

    run_electricity_source()
    payload = build_electricity_public()

    status = payload.get("status")

    if status == "ok":
        print("[OK] electricity -> public updated")
    elif status == "empty":
        print("[EMPTY] electricity -> public updated")
    else:
        print("[ERROR] electricity -> public update failed")


def update_pharmacies() -> None:
    run_pharmacies_source()
    payload = build_pharmacies_public()

    status = payload.get("status")

    if status == "ok":
        print("[OK] pharmacies -> public updated")
    elif status == "empty":
        print("[EMPTY] pharmacies -> public updated")
    else:
        print("[ERROR] pharmacies -> public update failed")


def update_water() -> None:
    run_water_source()
    path = build_water_public()
    print(f"[OK] water -> {path}")


def update_emergency_contacts() -> None:
    payload = build_emergency_public()

    status = payload.get("status")

    if status == "ok":
        print("[OK] emergency -> public updated")
    elif status == "empty":
        print("[EMPTY] emergency -> public updated")
    else:
        print("[ERROR] emergency -> public update failed")
