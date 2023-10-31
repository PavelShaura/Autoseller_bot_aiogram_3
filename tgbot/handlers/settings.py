from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.db.db_api import subs, photos
from tgbot.keyboards.inline import show_qr_keyboard, support_keyboard
from tgbot.lexicon.lexicon_ru import LEXICON_RU

settings_router = Router()


@settings_router.callback_query(
    F.data.contains("choose_os"), flags={"throttling_key": "callback"}
)
async def choose_os(call: CallbackQuery):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)
        return

    data: list[str] = call.data.split(":")
    os: str = data[1]
    print(os)
    if os in ["iphone", "android"]:
        await call.message.edit_text(
            text=LEXICON_RU["mobile_support"],
            reply_markup=show_qr_keyboard,
        )
    elif os in ["macos", "windows"]:
        await call.message.edit_text(
            text=LEXICON_RU["desc_support"],
            reply_markup=support_keyboard,
        )


@settings_router.callback_query(F.data.contains("show_qr"))
async def show_qr(call: CallbackQuery):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    user_data: Optional[dict] = await photos.find_one({"user_id": user_id})

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
