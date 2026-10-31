import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, User

from app.handlers.start import build_main_menu, router as start_router
from app.modules.market.router import LABELS, market_keyboard, open_market, market_placeholder, router as market_router


class MarketTests(unittest.IsolatedAsyncioTestCase):
    def test_menu_entry_and_legacy_removed(self):
        for lang in ("ru", "en", "tr"):
            buttons = [b for row in build_main_menu(lang).inline_keyboard for b in row]
            self.assertEqual(sum(b.callback_data == "market:menu" for b in buttons), 1)
            self.assertFalse(any(b.url == "https://t.me/alanya_rent07/16" for b in buttons))

    def test_market_buttons_all_languages(self):
        with patch.dict(os.environ, {"ALIMIND_SEARCH_URL": "https://alimindcity.com/search-ai/"}):
            for lang in ("ru", "en", "tr"):
                buttons = [b for row in market_keyboard(lang).inline_keyboard for b in row]
                self.assertEqual(len(buttons), 3)
                self.assertEqual(buttons[0].url, "https://alimindcity.com/search-ai/")
                self.assertEqual(buttons[1].callback_data, "market:goods")
                self.assertEqual(buttons[2].callback_data, "main:menu")
                self.assertEqual([b.text for b in buttons], list(LABELS[lang][:3]))

    def test_missing_search_url(self):
        with patch.dict(os.environ, {"ALIMIND_SEARCH_URL": ""}):
            button = market_keyboard("ru").inline_keyboard[0][0]
            self.assertEqual(button.callback_data, "market:search_unconfigured")

    async def test_market_handler(self):
        callback = SimpleNamespace(
            from_user=SimpleNamespace(id=42),
            message=SimpleNamespace(edit_text=AsyncMock()),
            answer=AsyncMock(),
        )
        with patch("app.modules.market.router.get_user_lang", return_value="ru"):
            await open_market(callback)
        callback.message.edit_text.assert_awaited_once()
        callback.answer.assert_awaited_once()

    async def test_goods_handler(self):
        callback = SimpleNamespace(
            from_user=SimpleNamespace(id=42),
            data="market:goods",
            message=SimpleNamespace(edit_text=AsyncMock()),
            answer=AsyncMock(),
        )
        with patch("app.modules.market.router.get_user_lang", return_value="ru"):
            await market_placeholder(callback)
        self.assertIn("Раздел готовится", callback.message.edit_text.await_args.args[0])
        callback.answer.assert_awaited_once()

    def test_router_registration_filters(self):
        dp = Dispatcher()
        dp.include_router(start_router)
        dp.include_router(market_router)
        self.assertIn(market_router, dp.sub_routers)
        self.assertGreaterEqual(len(market_router.callback_query.handlers), 2)


if __name__ == "__main__":
    unittest.main()
