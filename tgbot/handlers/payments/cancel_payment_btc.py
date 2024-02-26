import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.config import config
from tgbot.cryptopaylogic.conf_check import CHAT_ID_INDEX, USER_ID_INDEX, STATUS_INDEX
from tgbot.sqlite.database import db_manager
from tgbot.cryptopaylogic.delete_order import delete_sellix_order
from tgbot.keyboards.inline import back_to_menu

cancel_payment_btc_router = Router()


@cancel_payment_btc_router.callback_query(
    F.data.contains("btc_cancel"), StateFilter("waiting_bitcoin")
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
            success, message = await delete_sellix_order(
                config.tg_bot.selix_api_key, uniqid
            )
            if success:
                db_manager.update_order_status(uniqid, "Cancelled")
                await call.message.answer(
                    f"Заказ <code>{uniqid}</code> был успешно отменен.",
                    parse_mode="HTML",
                    reply_markup=back_to_menu,
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
