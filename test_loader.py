from app.modules import (
    load_all_objects,
    load_objects_by_category,
)

all_items = load_all_objects()
beauty_items = load_objects_by_category("beauty")
sport_items = load_objects_by_category("sport")

print("ALL ITEMS:", all_items)
print("ALL COUNT:", len(all_items))
print("BEAUTY ITEMS:", beauty_items)
print("BEAUTY COUNT:", len(beauty_items))
print("SPORT ITEMS:", sport_items)
print("SPORT COUNT:", len(sport_items))