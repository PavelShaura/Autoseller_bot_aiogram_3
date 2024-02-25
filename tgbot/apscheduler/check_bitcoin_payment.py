import logging
from datetime import datetime, timedelta
from typing import Any, Tuple

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.config import config
from tgbot.cryptopaylogic.conf_check import check_order_status, HASH_INDEX
from tgbot.sqlite.database import db_manager
from tgbot.cryptopaylogic.delete_order import delete_sellix_order
from tgbot.yoomoneylogic.check_payment_logic import (
    process_check_payment_and_subscription,
)


async def start_periodic_check(
    call: Any, chat_id: int, uniqid: str, user_id: int, amount: float
) -> None:
    """
    Perform periodic checks on an order's status and take appropriate actions.

    Args:
        call (Any): The call object.
        chat_id (int): The ID of the chat.
        uniqid (str): The unique identifier of the order.
        user_id (int): The ID of the user.
        amount (float): The amount associated with the order.

    Returns:
        None

    Performs periodic checks on the status of the specified order and takes appropriate actions based on the status
    and elapsed time since the order was placed. This function interacts with various components of the Telegram bot,
    including sending messages and updating the database.
    """
    job_id: str = db_manager.get_job_id(uniqid)
    job_context: str = db_manager.get_job_context(job_id)
    first_check_time: datetime = datetime.strptime(job_context, "%Y-%m-%d %H:%M:%S.%f")

    if not chat_id or not uniqid:
        logging.error("The chat ID or Uniqid is not present in the context of the job.")
        return

    now: datetime = datetime.now()

    time_diff: timedelta = now - first_check_time
    delete_after: timedelta = timedelta(hours=1)

    current_status, crypto_hash = await check_order_status(
        config.tg_bot.selix_api_key, uniqid
    )  # assuming `check_order_status` returns Tuple[str, str]

    if current_status:
        last_status: str = db_manager.get_order_status(uniqid)

        valid_transitions: list[Tuple[str, str], Tuple[str, str], Tuple[str, str]] = [
            ("PENDING", "WAITING_FOR_CONFIRMATIONS"),
            ("PENDING", "COMPLETED"),
            ("WAITING_FOR_CONFIRMATIONS", "COMPLETED"),
        ]

        if (last_status, current_status) in valid_transitions:
            message: str = (
                f"Для идентификатора <code>{uniqid}</code> \n"
                f"статус изменен с <code>{last_status}</code> \n"
                f"на <code>{current_status}</code>"
            )
            await call.message.answer(text=message, parse_mode="HTML")
            logging.info(
                f"Order {uniqid} status changed from {last_status} to {current_status}"
            )
            db_manager.update_order_status(uniqid, current_status)

            order_details: Any = db_manager.get_order_details(uniqid)

            if (
                crypto_hash
                and order_details
                and order_details[HASH_INDEX] != crypto_hash
            ):
                db_manager.update_order_hash(uniqid, crypto_hash)
                await call.message.answer(
                    text=f"Hash транзакции: <code>{crypto_hash}</code>",
                    parse_mode="HTML",
                )

        if last_status == "PENDING" and time_diff > delete_after:
            success: bool
            message: str
            success, message = await delete_sellix_order(
                config.tg_bot.selix_api_key, uniqid
            )
            if success:
                await call.message.answer(
                    text=f"Заказ <code>{uniqid}</code> был автоматически отменен из-за таймаута.",
                )
                db_manager.update_order_status(uniqid, "Cancelled")
                logging.info(
                    f"Order {uniqid} has been automatically cancelled due to timeout, Placed by: {chat_id}"
                )
                scheduler.remove_job(job_id)
            else:
                logging.error(
                    f"Failed to automatically cancel order {uniqid}: {message}"
                )

        if current_status == "COMPLETED":
            await process_check_payment_and_subscription(call, user_id, amount)
            logging.info(
                f"Order {uniqid} for {amount} successfully executed for {user_id}. Removing the Job"
            )
            scheduler.remove_job(job_id)
        elif current_status == "VOIDED":
            logging.info(
                f"Order {uniqid} Was Cancelled, Buyer: {chat_id}. Removing the Job"
            )
            scheduler.remove_job(job_id)
    else:
        logging.error(
            f"No current status for order {uniqid}. It might be an API error or network issue."
        )
