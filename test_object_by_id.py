from app.modules import load_object_by_id

item_ok = load_object_by_id("beauty_olesya_hair")
item_missing = load_object_by_id("no_such_id")

print("FOUND:", item_ok)
print("MISSING:", item_missing)