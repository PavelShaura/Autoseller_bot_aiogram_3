from datetime import datetime
from typing import Optional, Union

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.inline import os_keyboard
from tgbot.mongo_db.db_api import subs
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

user_settings_router = Router()


@user_settings_router.callback_query(F.data == "settings")
@user_settings_router.message(F.text == "Мои настройки")
async def user_settings(query: Union[Message, CallbackQuery]):
    user_id: int = query.from_user.id

    message: Message = query if isinstance(query, Message) else query.message

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if not sub:
        await message.answer(text=LEXICON_RU["no_sub"])
    else:
        await message.answer(
            text=LEXICON_RU["yes_sub"],
            disable_web_page_preview=True,
            reply_markup=os_keyboard,
        )
