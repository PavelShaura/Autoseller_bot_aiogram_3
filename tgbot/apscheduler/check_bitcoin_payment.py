import logging
from datetime import datetime, timedelta

from tgbot.apscheduler.apscheduler import scheduler
from tgbot.config import config
from tgbot.cryptopaylogic.conf_check import check_order_status, HASH_INDEX
from tgbot.sqlite.database import db_manager
from tgbot.cryptopaylogic.delete_order import delete_sellix_order
from tgbot.yoomoneylogic.check_payment_logic import (
    process_check_payment_and_subscription,
)


async def start_periodic_check(call, chat_id, uniqid, user_id, amount):

    job_id = db_manager.get_job_id(uniqid)
    job_context = db_manager.get_job_context(job_id)
    first_check_time = datetime.strptime(job_context, '%Y-%m-%d %H:%M:%S.%f')

    if not chat_id or not uniqid:
        logging.error("The chat ID or Uniqid is not present in the context of the job.")
        return

    now = datetime.now()

    # Вычисляем разницу во времени
    time_diff = now - first_check_time
    delete_after = timedelta(seconds=30)

    current_status, crypto_hash = check_order_status(
        config.tg_bot.selix_api_key, uniqid
    )
    if current_status:
        last_status = db_manager.get_order_status(uniqid)

        valid_transitions = [
            ("PENDING", "WAITING_FOR_CONFIRMATIONS"),
            ("PENDING", "COMPLETED"),
            ("WAITING_FOR_CONFIRMATIONS", "COMPLETED"),
        ]

        if (last_status, current_status) in valid_transitions:
            message = (
                f"Для идентификатора <code>{uniqid}</code> \n"
                f"статус изменен с <code>{last_status}</code> \n"
                f"на <code>{current_status}</code>"
            )
            await call.message.answer(text=message, parse_mode="HTML")
            logging.info(
                f"Order {uniqid} status changed from {last_status} to {current_status}"
            )
            db_manager.update_order_status(uniqid, current_status)

            order_details = db_manager.get_order_details(uniqid)
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
            success, message = delete_sellix_order(config.tg_bot.selix_api_key, uniqid)
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
