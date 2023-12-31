from datetime import datetime, timedelta
from typing import Optional
import os

from aiogram import Router, F, Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import config
from tgbot.db.db_api import subs
from tgbot.services.apsched import send_message_trial
from tgbot.services.successful_payment_logic import process_trial_subscription

from tgbot.utils.get_trial_image import get_trial_image_filename

from tgbot.keyboards.inline import (
    support_keyboard,
    settings_keyboard,
)
from tgbot.keyboards.reply import choose_plan_keyboard

trial_router = Router()


@trial_router.message(F.text.in_({"🔥 АКЦИЯ!!! 🔥 ⏱ Пробный период на 3 дня"}))
async def process_pay(query: Message, bot: Bot, apscheduler: AsyncIOScheduler):
    user_id: int = query.from_user.id
    user = query.from_user.full_name
    username = query.from_user.username

    sub: Optional[dict] = await subs.find_one(filter={"user_id": user_id})

    if sub:
        sub_flag = sub.get("client_id")
        if len(sub_flag) > 10:
            await query.answer(
                text="Извините! Вы уже воспользовались пробным периодом 😪"
                "Акция доступна только один раз",
                reply_markup=choose_plan_keyboard,
            )
        else:
            await query.answer(
                text="✅ Вы уже оформляли подписку\n"
                "Акция доступна только новым пользователям",
                reply_markup=choose_plan_keyboard,
            )
    else:
        image_filename = ""
        client_id = ""
        pk = ""

        async for image in get_trial_image_filename():
            image_filename = image
            break

        try:
            pk = image_filename.split("/")[3].split(".")[0]
            client_id = "Client_№" + pk + "_TRIAL"

        except Exception as e:
            print(e)

        if not os.path.exists(image_filename):
            await query.answer(
                text="Извините! Лимит на бесплатные подписки закончился 😪\n"
                "Ждите анонса новой акции в наших соц сетях 🙈",
                reply_markup=support_keyboard,
            )
        else:
            await process_trial_subscription(
                query, settings_keyboard, client_id, image_filename, pk
            )

            apscheduler.add_job(
                send_message_trial,
                trigger="date",
                run_date=datetime.now() + timedelta(seconds=10810),
                # run_date=datetime.now() + timedelta(seconds=10),
                kwargs={
                    "bot": bot,
                    "chat_id": config.tg_bot.channel_id,
                    "user": user,
                    "username": username,
                    "client_id": client_id,
                },
            )
