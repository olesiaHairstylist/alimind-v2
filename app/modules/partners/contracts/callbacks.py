from __future__ import annotations

PARTNER_CLICK_PREFIX = "partner:click:"


def build_partner_click_cb(partner_id: str) -> str:
    return f"{PARTNER_CLICK_PREFIX}{partner_id}"


def is_partner_click_cb(data: str | None) -> bool:
    return bool(data and data.startswith(PARTNER_CLICK_PREFIX))


def parse_partner_click_cb(data: str | None) -> str | None:
    if not is_partner_click_cb(data):
        return None

    partner_id = str(data)[len(PARTNER_CLICK_PREFIX):].strip()
    return partner_id or None

