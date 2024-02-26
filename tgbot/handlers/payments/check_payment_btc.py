import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.sqlite.database import db_manager
from tgbot.phrasebook.lexicon_ru import TRANSACTIONS

check_payment_btc_router = Router()


@check_payment_btc_router.callback_query(
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
