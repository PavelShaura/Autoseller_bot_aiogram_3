from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message

from tgbot.keyboards.inline import show_qr_keyboard
from tgbot.keyboards.reply import choose_plan_keyboard
from tgbot.mongo_db.db_api import subs

profile_user_router = Router()


@profile_user_router.message(F.text == "Профиль")
async def process_profile(message: Message):
    user_id: int = message.from_user.id
    name: str = message.from_user.first_name
    username: str = (
        f"<b>Юзернейм:</b> {message.from_user.username}\n"
        if message.from_user.username
        else ""
    )

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if sub:
        end_date: str = sub["end_date"].strftime("%d.%m.%Y")
        sub_text: str = f"Статус подписки: ✅ активирована\nСрок действия: до {end_date}"
        reply_markup = show_qr_keyboard
    else:
        sub_text = "Статус подписки: ❌ не активирована"
        reply_markup = choose_plan_keyboard

    text = f"Профиль\n\nВаш ID: {user_id}\nИмя: {name}\n{username}\n\n{sub_text}\n"

    await message.answer(text=text, reply_markup=reply_markup)
