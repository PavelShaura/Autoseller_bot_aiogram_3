import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from apscheduler.job import Job

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.apscheduler.check_bitcoin_payment import start_periodic_check
from tgbot.config import config
from tgbot.cryptopaylogic.create_order import create_order
from tgbot.sqlite.database import db_manager
from tgbot.mongo_db.db_api import subs

from tgbot.keyboards.inline import status_or_cancel_payment_bitcoin

payment_bitcoin_router = Router()


@payment_bitcoin_router.callback_query(
    F.data.contains("cryptopay"),
    StateFilter("check_plan"),
    flags={"throttling_key": "payment"},
)
async def invoicing_for_payment_bitcoin(call: CallbackQuery, state: FSMContext):
    user_id: int = call.from_user.id
    username = call.from_user.username
    message = call.message
    chat_id = message.chat.id

    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )
    sub_text = ""
    if sub:
        sub_text = "\n\n<i> ✅ У вас уже активирована подписка. При оплате подписка будет продлена. </i> \n\n"

    state_data = await state.get_data()
    current_price = state_data.get("current_price")
    value = int(current_price)

    gateway = "BITCOIN"

    address, amount, uniqid, protocol, rub_value = await create_order(
        config.tg_bot.selix_api_key, gateway, value
    )

    await call.message.edit_text(
        text=f"Оплата <b>{gateway}</b>  🪙\n\n{sub_text}"
        f"Пополните <code>{amount}</code> <b>BTC</b>\n"
        f"<b>На кошелек:</b> \n<code>{address}</code>\n\n"
        f"<b>Ваш идентификатор заказа:</b> <code>{uniqid}</code>\n\n"
        f"<b>Бот автоматически проверяет статус платежа.</b>\n\n"
        f"<i>После одного подтверждения Вам придет QR-код для подключения "
        f"и будет доступно меню настроек</i>",
        parse_mode="HTML",
        reply_markup=status_or_cancel_payment_bitcoin,
    )
    job: Job = scheduler.add_job(
        start_periodic_check,
        trigger="interval",
        seconds=15,
        kwargs={
            "chat_id": chat_id,
            "uniqid": uniqid,
            "user_id": user_id,
            "amount": value,
            "call": call,
        },
    )
    job_id = job.id
    db_manager.insert_order(
        chat_id,
        user_id,
        username,
        uniqid,
        "PENDING",
        protocol,
        rub_value,
        "None",
        job_id,
    )
    logging.info(f"{username} added to btc_checker_DB ID {user_id}")
    db_manager.update_job_context(job_id, date)
    await state.set_state("waiting_bitcoin")
    await state.update_data(uniqid=uniqid)
