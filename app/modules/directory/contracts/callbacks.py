from __future__ import annotations


DIRECTORY_MENU_CB = "directory:menu"
DIRECTORY_BACK_CB = "directory:back"


def build_directory_category_cb(category_id: str) -> str:
    return f"directory:category:{category_id}"


def is_directory_category_cb(data: str | None) -> bool:
    return bool(data and data.startswith("directory:category:"))


def parse_directory_category_cb(data: str) -> str | None:
    prefix = "directory:category:"
    if not data.startswith(prefix):
        return None

    category_id = data[len(prefix):].strip()
    return category_id or None


def build_directory_subcategory_cb(category_id: str, subcategory_id: str) -> str:
    return f"directory:subcategory:{category_id}:{subcategory_id}"


def is_directory_subcategory_cb(data: str | None) -> bool:
    return bool(data and data.startswith("directory:subcategory:"))


def parse_directory_subcategory_cb(data: str) -> tuple[str, str] | None:
    prefix = "directory:subcategory:"
    if not data.startswith(prefix):
        return None

    raw = data[len(prefix):].strip()
    parts = raw.split(":", maxsplit=1)

    if len(parts) != 2:
        return None

    category_id, subcategory_id = parts[0].strip(), parts[1].strip()
    if not category_id or not subcategory_id:
        return None

    return category_id, subcategory_id


def build_directory_open_cb(object_id: str) -> str:
    return f"directory:open:{object_id}"


def is_directory_open_cb(data: str | None) -> bool:
    return bool(data and data.startswith("directory:open:"))


def parse_directory_open_cb(data: str) -> str | None:
    prefix = "directory:open:"
    if not data.startswith(prefix):
        return None

    object_id = data[len(prefix):].strip()
    return object_id or None