import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import support_keyboard
from tgbot.mongo_db.db_api import subs, files
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

show_qr_router = Router()


@show_qr_router.callback_query(F.data.contains("show_qr"))
async def show_qr(call: CallbackQuery):
    user_id: int = call.from_user.id
    username = call.from_user.username
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    user_data: Optional[dict] = await files.find_one({"user_id": user_id})

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)
        return
    else:
        if user_data:
            photo_id: str = user_data.get("photo_id")

            await call.message.answer_photo(
                photo=photo_id, caption=f"Ваш QR-код для подключения ⤴️"
            )
        else:
            await call.message.answer(
                text=LEXICON_RU["empty_qr"],
                reply_markup=support_keyboard,
            )
            logging.info(f"For {user_id} {username} QR- code didn't send")
