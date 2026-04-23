from app.modules.directory.services.loader import load_subcategories as load_subcategories_by_category
from app.modules.directory.contracts.categories import SUBCATEGORY_TITLES


def get_subcategory_title(category_id: str, subcategory_id: str) -> str:
    items = load_subcategories_by_category(category_id)

    for item in items:
        if item.get("id") == subcategory_id:
            return (
                item.get("title")
                or SUBCATEGORY_TITLES.get(subcategory_id)
                or subcategory_id
            )

    return SUBCATEGORY_TITLES.get(subcategory_id, subcategory_id)