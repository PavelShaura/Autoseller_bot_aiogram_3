import logging
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.apscheduler.send_to_admin_group import notification_payment_cleared
from tgbot.config import config
from tgbot.yoomoneylogic.check_payment_logic import (
    process_check_payment_and_subscription,
)
from tgbot.yoomoneylogic.yoomoney_api import PaymentYooMoney, NoPaymentFound


check_payment_u_money_router = Router()


@check_payment_u_money_router.callback_query(
    F.data.contains("check_payment"),
    StateFilter("check_payment"),
    flags={"throttling_key": "callback"},
)
async def check_payment(call: CallbackQuery, bot: Bot, state: FSMContext):
    user = call.from_user.full_name
    username = call.from_user.username
    user_id: int = call.from_user.id
    data: list[str] = call.data.split(":")
    payment_id: str = data[1]

    state_data: dict[str, Optional[str]] = await state.get_data()
    state_payment_id: Optional[str] = state_data.get("payment_id")
    amount: Optional[int] = state_data.get("amount")

    if payment_id != state_payment_id:
        await call.answer("Вы начинали новую оплату ниже.")
        return

    payment = PaymentYooMoney(id=payment_id, amount=amount)
    try:
        amount = payment.check_payment()
    except NoPaymentFound:
        await call.answer("Оплата не найдена, сначала выполните оплату.")
    else:
        await process_check_payment_and_subscription(call, user_id, amount)
        await state.clear()

        logging.info(f"Good news! {user} successfully subscribed! Amount {amount}")

        scheduler.add_job(
            notification_payment_cleared,
            trigger="date",
            # run_date=datetime.now() + timedelta(seconds=10810),# For production (time difference on the server -3 hours)
            run_date=datetime.now() + timedelta(seconds=10),
            kwargs={
                "bot": bot,
                "chat_id": config.tg_bot.channel_id,
                "amount": amount,
                "user": user,
                "username": username,
            },
        )
    finally:
        logging.info(f"User: {user} checking payment")