from __future__ import annotations

import runpy
from typing import Any

from app.modules import write_health
from app.modules import read_public_health


def update_all() -> dict[str, Any]:
    try:
        try:
            runpy.run_module(
                "app.modules.city_events.services.update_city_events",
                run_name="__main__"
            )
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 0
            if code not in (0, None):
                return {
                    "status": "error",
                    "message": f"update_city_events exited with code {code}"
                }

        status_map = read_public_health()


        write_health(status_map)

        return {
            "status": "ok",
            "message": "city_events updated + health saved",
            "sources": status_map,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }