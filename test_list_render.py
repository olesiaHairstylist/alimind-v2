from app.modules import load_objects_by_category
from app.modules import render_objects_list

items = load_objects_by_category("beauty")
text = render_objects_list("💇 Красота", items)

print(text)