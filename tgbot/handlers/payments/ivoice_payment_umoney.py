import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.mongo_db.db_api import subs

from tgbot.yoomoneylogic.yoomoney_api import PaymentYooMoney
from tgbot.keyboards.inline import payment_keyboard

payment_u_money_router = Router()


@payment_u_money_router.callback_query(
    F.data.contains("u_money"),
    StateFilter("check_plan"),
    flags={"throttling_key": "payment"},
)
async def invoicing_for_payment_u_money(call: CallbackQuery, state: FSMContext):
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
