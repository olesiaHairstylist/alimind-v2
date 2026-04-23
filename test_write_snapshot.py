from app.modules import write_pharmacies_snapshot
from app.modules import build_directory_category_menu

path = write_pharmacies_snapshot(["2", "3", "5", "9"])

print("WRITTEN:", path)
@router.message(Command("dir_test"))
async def test_directory_menu(message: Message):
    await message.answer(
        "Категории услуг:",
        reply_markup=build_directory_category_menu()
    )