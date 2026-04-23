from app.modules import (
    DIRECTORY_MENU_CB,
    DIRECTORY_BACK_CB,
    build_directory_category_cb,
    build_directory_open_cb,
)

print("MENU:", DIRECTORY_MENU_CB)
print("BACK:", DIRECTORY_BACK_CB)
print("CATEGORY:", build_directory_category_cb("beauty"))
print("OPEN:", build_directory_open_cb("beauty_olesya_hair"))