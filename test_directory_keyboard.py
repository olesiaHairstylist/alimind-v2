from app.modules import build_directory_categories_kb

kb = build_directory_categories_kb()
print(kb.model_dump())