DEFAULT_V3_WEIGHT_MODE = "preview"

WEIGHT_MODES = {
    "off": 0.0,
    "preview": 0.2,
    "medium": 0.35,
    "strong": 0.5,
}


def get_v3_weight_mode() -> str:
    return DEFAULT_V3_WEIGHT_MODE


def get_v3_preview_weight() -> float:
    mode = str(get_v3_weight_mode() or DEFAULT_V3_WEIGHT_MODE).strip().lower()
    if mode not in WEIGHT_MODES:
        mode = DEFAULT_V3_WEIGHT_MODE
    return float(WEIGHT_MODES.get(mode, WEIGHT_MODES[DEFAULT_V3_WEIGHT_MODE]))
