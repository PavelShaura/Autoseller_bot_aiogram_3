from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "default": {
            "cache": TTLCache(maxsize=10_000, ttl=5),
            "text": "🥵 Не пишите так часто!",
        },
        "callback": {
            "cache": TTLCache(maxsize=10_000, ttl=10),
            "text": "🥵 Не так часто!",
        },
        "payment": {
            "cache": TTLCache(maxsize=10_000, ttl=15),
            "text": "🙌 Вы недавно уже запрашивали ссылку на оплату. Подождите немного.",
        },
    }

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.caches:
            throttling = self.caches[throttling_key]
            if event.from_user.id in throttling["cache"]:
                text = throttling["text"]
                await event.answer(text)
                return
            else:
                throttling["cache"][event.from_user.id] = None
        return await handler(event, data)
