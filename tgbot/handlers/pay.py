from datetime import datetime, timedelta
import os
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from pymongo import ReturnDocument
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import config
from tgbot.db.db_api import payments, subs, files
from tgbot.lexicon.lexicon_ru import LEXICON_RU
from tgbot.services.get_image import get_next_image_filename
from tgbot.services.yoomoney_api import PaymentYooMoney, NoPaymentFound
from tgbot.keyboards.inline import settings_keyboard, support_keyboard
from tgbot.services.apsched import send_message_pay


pay_router = Router()


@pay_router.callback_query(
    F.data.contains("check_payment"),
    StateFilter("check_payment"),
    flags={"throttling_key": "callback"}
)
async def check_payment(call: CallbackQuery, bot: Bot, state: FSMContext, apscheduler: AsyncIOScheduler):
    user = call.from_user.full_name
    username = call.from_user.username
    user_id: int = call.from_user.id
    data: list[str] = call.data.split(":")
    payment_id: str = data[1]

    state_data: dict[str, Optional[str]] = await state.get_data()
    state_payment_id: Optional[str] = state_data.get("payment_id")
    amount: Optional[int] = state_data.get("amount")
    print(amount)
    if payment_id != state_payment_id:
        await call.answer("Вы начинали новую оплату ниже.")
        return

    payment = PaymentYooMoney(id=payment_id, amount=amount)
    try:
        if user_id in config.tg_bot.admin_ids:
            amount = payment.__dict__["amount"]  # Заглушка для теста(admin)
        else:
            amount = payment.check_payment()  # Проверка оплаты
    except NoPaymentFound:
        await call.answer("Оплата не найдена, сначала выполните оплату.")
    else:

        apscheduler.add_job(send_message_pay, trigger='date', run_date=datetime.now() + timedelta(seconds=5),
                            kwargs={'bot': bot,
                                    'chat_id': config.tg_bot.channel_id,
                                    "amount": amount,
                                    "user": user,
                                    "username": username})

        date: datetime = datetime.now()
        await payments.insert_one(
            {
                "user_id": user_id,
                "amount": amount,
                "payment_type": "YooMoney",
                "date": date,
            }
        )

        sub: dict = await subs.find_one(
            filter={"user_id": user_id, "end_date": {"$gt": date}}
        )
        if sub:
            end_date: datetime = sub["end_date"]

            if amount == 600:
                end_date += timedelta(days=90)
            elif amount == 900:
                end_date += timedelta(days=180)
            elif amount == 1350:
                end_date += timedelta(days=365)

            sub = await subs.find_one_and_update(
                filter={"user_id": user_id, "end_date": {"$gt": date}},
                update={"$set": {"end_date": end_date}},
                return_document=ReturnDocument.AFTER,
            )

            end_date_str: str = sub["end_date"].strftime("%d.%m.%Y")

            image_filename = ""
            client_id = None
            pk = None
            async for image in get_next_image_filename():
                image_filename = image
                break

            try:
                pk = image_filename.split('/')[2].split('.')[0]
                client_id = "Client_№" + pk
            except Exception:
                pass

            if not os.path.exists(image_filename):
                await call.message.answer(
                    text=LEXICON_RU["empty_qr"],
                    reply_markup=support_keyboard,
                )
                return

            image_from_pc: FSInputFile = FSInputFile(image_filename)

            result = await call.message.answer_photo(
                photo=image_from_pc,
                caption="✅  Оплата прошла успешно!!! \n\n\n"
                "Ваш QR - код для подключения ⤴️ \n"
                "Используйте его по истечению срока предыдущего подключения\n\n"
                f"Общий срок действия подписки: до {end_date_str}\n\n"
                f"Перейдите в меню настроек для подключения",
                reply_markup=settings_keyboard
            )

            os.remove(image_filename)

            await files.update_one(
                {"user_id": user_id},
                {"$set": {"photo_id": result.photo[-1].file_id,
                          "pk": pk}
                 }
            )
            update_sub = await subs.update_one(
                filter={"user_id": user_id, "end_date": {"$gt": date}},
                update={"$set": {"client_id": client_id}},
            )
        else:
            await subs.delete_many(filter={"user_id": user_id})

            end_date: datetime = datetime.now()

            if amount == 600:
                end_date += timedelta(days=90)
            elif amount == 900:
                end_date += timedelta(days=180)
            elif amount == 1350:
                end_date += timedelta(days=365)

            start_date: datetime = datetime.now()

            await subs.insert_one(
                document={
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

            end_date_str: str = end_date.strftime("%d.%m.%Y")

            image_filename = ""
            client_id = None
            pk = None
            async for image in get_next_image_filename():
                image_filename = image
                break

            try:
                pk = image_filename.split('/')[2].split('.')[0]
                client_id = "Client_№" + pk
            except Exception:
                pass
            if not os.path.exists(image_filename):
                await call.message.answer(
                    text=LEXICON_RU["empty_qr"],
                    reply_markup=support_keyboard,
                )

            image_from_pc = FSInputFile(image_filename)

            result = await call.message.answer_photo(
                photo=image_from_pc,
                caption=f"✅  Оплата прошла успешно!!! \n\n\n"
                f"Ваш QR - код для подключения ⤴️ \n\n"
                f"<b>Срок действия:</b> до {end_date_str}\n\n"
                f"Перейдите в меню настроек для подключения",
                reply_markup=settings_keyboard,
            )

            await files.insert_one(
                {"user_id": user_id,
                 "photo_id": result.photo[-1].file_id,
                 "pk": pk}
            )
            update_sub = await subs.update_one(
                filter={"user_id": user_id, "end_date": {"$gt": date}},
                update={"$set": {"client_id": client_id}},
            )
            os.remove(image_filename)

        await state.clear()
