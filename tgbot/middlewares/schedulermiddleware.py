from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from tgbot.apscheduler.apscheduler import scheduler


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, apscheduler: scheduler):
        self.apscheduler = apscheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["apscheduler"] = self.apscheduler
        return await handler(event, data)
