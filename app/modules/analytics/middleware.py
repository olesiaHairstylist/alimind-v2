from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Update

from app.modules.analytics.storage import log_event


class AnalyticsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            if isinstance(event, Update):
                if event.message and event.message.from_user:
                    user = event.message.from_user

                    log_event({
                        "type": "message",
                        "user_id": user.id,
                        "text": event.message.text,
                    })

                elif event.callback_query and event.callback_query.from_user:
                    user = event.callback_query.from_user

                    log_event({
                        "type": "callback",
                        "user_id": user.id,
                        "data": event.callback_query.data,
                    })

        except Exception:
            pass

        return await handler(event, data)