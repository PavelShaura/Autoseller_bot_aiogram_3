import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from apscheduler.job import Job

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.apscheduler.check_bitcoin_payment import start_periodic_check
from tgbot.config import config
from tgbot.cryptopaylogic.conf_check import CHAT_ID_INDEX, USER_ID_INDEX, STATUS_INDEX
from tgbot.cryptopaylogic.create_order import create_order
from tgbot.sqlite.database import db_manager
from tgbot.cryptopaylogic.delete_order import delete_sellix_order
from tgbot.mongo_db.db_api import subs
from tgbot.phrasebook.lexicon_ru import TRANSACTIONS

from tgbot.yoomoneylogic.yoomoney_api import PaymentYooMoney
from tgbot.keyboards.inline import payment_keyboard, status_or_cancel_payment_bitcoin

invoicing_for_payment_router = Router()


@invoicing_for_payment_router.callback_query(
    F.data.contains("u_money"),
    StateFilter("check_plan"),
    flags={"throttling_key": "payment"},
)
async def invoicing_for_payment_umoney(call: CallbackQuery, state: FSMContext):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )
    sub_text = ""
    if sub:
        sub_text = "\n\n<i> ✅ У вас уже активирована подписка. При оплате подписка будет продлена. </i> \n\n"

    state_data = await state.get_data()
    current_price = state_data.get("current_price")
    month = state_data.get("month")

    amount = int(current_price)

    text = (
        f"<b>Оплата картой</b> 💳\n\n"
        f"Цена за <b>{month}</b>:  <code>{amount} рублей </code> {sub_text}\n\n"
        f"Оплата банковской картой через платежную систему ЮМани.\n"
        f"Это надёжно и удобно.\n\n"
        f"<i>После оплаты нажмите 'Проверить платеж' после чего "
        f"Вам придет QR-код для подключения и будет доступно меню настроек</i>"
    )

    payment = PaymentYooMoney(amount=amount)
    payment.create()

    try:
        await call.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=payment_keyboard(
                payment_id=payment.id, invoice=payment.invoice
            ),
        )
    except TelegramBadRequest as e:
        logging.info(f"Exception {e}, user_id {user_id}")

    await state.set_state("check_payment")
    await state.update_data(payment_id=payment.id, amount=payment.amount)


@invoicing_for_payment_router.callback_query(
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

    address, amount, uniqid, protocol, rub_value = create_order(
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
            "bot": Bot,
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
    await state.set_state("waiting_bitcoin")
    await state.update_data(uniqid=uniqid)


@invoicing_for_payment_router.callback_query(
    F.data.contains("btc_status"),
    StateFilter("waiting_bitcoin"),
    flags={"throttling_key": "default"},
)
async def check_status_for_payment_bitcoin(
    call: CallbackQuery,
    state: FSMContext,
):
    user_id: int = call.from_user.id
    username = call.from_user.username
    state_data = await state.get_data()
    uniqid = state_data.get("uniqid")
    order_status = db_manager.get_order_status(uniqid)
    if order_status:
        await call.message.answer(
            f"Статус заказа ⏱ \n\n"
            f"Идентификатор заказа: <code>{uniqid}</code>\n"
            f"Статус:   <code>{TRANSACTIONS[order_status]}</code>",
            parse_mode="HTML",
        )
        logging.info(
            f"{username} - {user_id}: Check status {uniqid} - {TRANSACTIONS[order_status]}"
        )
    else:
        await call.message.answer(
            f"Невозможно получить статус. Возможно заказ <code>{uniqid}</code> уже отменен"
        )
        logging.error(
            f"{username} - {user_id}: Executed /status, failed to get status."
        )


@invoicing_for_payment_router.callback_query(
    F.data.contains("btc_cancel"),
    StateFilter("waiting_bitcoin"),
    flags={"throttling_key": "default"},
)
async def cancel_payment_bitcoin(
    call: CallbackQuery,
    state: FSMContext,
):
    user_id: int = call.from_user.id
    username = call.from_user.username
    message = call.message
    chat_id = message.chat.id
    state_data = await state.get_data()
    uniqid = state_data.get("uniqid")
    order_details = db_manager.get_order_details(uniqid)

    if (
        order_details
        and order_details[CHAT_ID_INDEX] == chat_id
        and order_details[USER_ID_INDEX] == user_id
    ):
        if order_details[STATUS_INDEX].upper() == "PENDING":
            success, message = delete_sellix_order(config.tg_bot.selix_api_key, uniqid)
            if success:
                db_manager.update_order_status(uniqid, "Cancelled")
                await call.message.answer(
                    f"Заказ <code>{uniqid}</code> был успешно отменен.",
                    parse_mode="HTML",
                )
                logging.info(
                    f"{username} - {user_id} Cancelled order {uniqid} -> successfully cancelled."
                )
            else:
                await call.message.answer(
                    f"Не удалось отменить заказ <code>{uniqid}</code>: {message}",
                    parse_mode="HTML",
                )
                logging.error(
                    f"{username} - {user_id} Failed to cancel order {uniqid}: {message}"
                )
        elif order_details[STATUS_INDEX].upper() == "CANCELLED":
            await call.message.answer(
                f"Заказ <code>{uniqid}</code> уже отменен.", parse_mode="HTML"
            )
        else:
            await call.message.answer("Заказ не может быть отменен.")
    else:
        await call.message.answer("У вас нет разрешения на отмену этого заказа")
        logging.info(
            f"{username} - {user_id} Tried to cancel an order he didn't place."
        )
