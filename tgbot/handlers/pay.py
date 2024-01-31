from datetime import datetime, timedelta
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pymongo import ReturnDocument
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import config
from tgbot.db.db_api import payments, subs, trial
from tgbot.services.successful_payment_logic import (
    process_successful_re_subscription_payment,
    process_successful_first_subscription_payment,
)
from tgbot.external_services.yoomoney_api import PaymentYooMoney, NoPaymentFound
from tgbot.keyboards.inline import settings_keyboard, support_keyboard
from tgbot.services.apsched import send_message_pay

pay_router = Router()

SUBSCRIBE_TIMELINE = {582.0: 90, 873.0: 180, 1309.5: 365}


@pay_router.callback_query(
    F.data.contains("check_payment"),
    StateFilter("check_payment"),
    flags={"throttling_key": "callback"},
)
async def check_payment(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    apscheduler: AsyncIOScheduler(timezone="Europe/Moscow"),
):
    user = call.from_user.full_name
    username = call.from_user.username
    user_id: int = call.from_user.id

    data: list[str] = call.data.split(":")
    payment_id: str = data[1]

    state_data: dict[str, Optional[str]] = await state.get_data()
    state_payment_id: Optional[str] = state_data.get("payment_id")
    amount: Optional[int] = state_data.get("amount")

    date: datetime = datetime.now()

    if payment_id != state_payment_id:
        await call.answer("Вы начинали новую оплату ниже.")
        return

    payment = PaymentYooMoney(id=payment_id, amount=amount)
    try:
        amount = payment.check_payment()
    except NoPaymentFound:
        await call.answer("Оплата не найдена, сначала выполните оплату.")
    else:
        trials: dict = await trial.find_one(filter={"user_id": user_id})

        try:
            trial_flag = trials.get("trial_flag")
            if trial_flag == "on":
                await trial.update_one(
                    filter={"user_id": user_id},
                    update={"$set": {"trial_flag": "Utilized"}},
                )
        except Exception as e:
            print(e)

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
            end_date += timedelta(days=SUBSCRIBE_TIMELINE[amount])

            sub = await subs.find_one_and_update(
                filter={"user_id": user_id, "end_date": {"$gt": date}},
                update={"$set": {"end_date": end_date}},
                return_document=ReturnDocument.AFTER,
            )

            end_date_str: str = sub["end_date"].strftime("%d.%m.%Y")

            await process_successful_re_subscription_payment(
                call, end_date_str, support_keyboard, settings_keyboard
            )
        else:
            await subs.delete_many(filter={"user_id": user_id})
            start_date: datetime = date
            end_date = start_date + timedelta(days=SUBSCRIBE_TIMELINE[amount])

            await subs.insert_one(
                document={
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

            end_date_str: str = end_date.strftime("%d.%m.%Y")

            await process_successful_first_subscription_payment(
                call, end_date_str, support_keyboard, settings_keyboard
            )

        await state.clear()

        apscheduler.add_job(
            send_message_pay,
            trigger="date",
            run_date=datetime.now() + timedelta(seconds=10810),
            kwargs={
                "bot": bot,
                "chat_id": config.tg_bot.channel_id,
                "amount": amount,
                "user": user,
                "username": username,
            },
        )
