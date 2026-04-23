from __future__ import annotations



from app.modules import run_fetch as run_water_fetch
from app.modules import run_fetch as run_pharmacies_fetch
from app.modules import build_electricity_payload
from app.modules import save_electricity_payload


from app.modules import save_electricity_payload

def main() -> int:
    print("CITY_EVENTS_UPDATE_START")

    # PHARMACIES
    try:
        path = run_pharmacies_fetch()
        print(f"[OK] pharmacies -> {path}")
    except Exception as e:
        print(f"[ERROR] pharmacies -> {e}")

    # ELECTRICITY
    try:
        payload = build_electricity_payload()
        path = save_electricity_payload(payload)

        status = payload.get("status")

        if status == "ok":
            print(f"[OK] electricity -> {path}")
        elif status == "empty":
            print("[EMPTY] electricity")
        else:
            print("[ERROR] electricity source failed")

    except Exception as e:
        print(f"[ERROR] electricity -> {e}")

    # WATER
    try:
        path = run_water_fetch()
        print(f"[OK] water -> {path}")
    except Exception as e:
        print(f"[ERROR] water -> {e}")

    print("CITY_EVENTS_UPDATE_DONE")
    return 0
def update_electricity() -> None:
    payload = build_electricity_payload()
    save_electricity_payload(payload)

    status = payload.get("status")

    if status == "ok":
        print("[OK] electricity -> saved")
    elif status == "empty":
        print("[EMPTY] electricity")
    else:
        print("[ERROR] electricity source failed")

if __name__ == "__main__":
    update_electricity()
    raise SystemExit(main())
