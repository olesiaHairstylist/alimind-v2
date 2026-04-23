from app.modules import load_objects_by_category
from app.modules import render_object_card

items = load_objects_by_category("beauty")

if items:
    text = render_object_card(items[0])
    print(text)
else:
    print("NO ITEMS")
    print(items[0])