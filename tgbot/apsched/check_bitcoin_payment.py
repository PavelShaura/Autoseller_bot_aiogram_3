import logging
from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import config
from tgbot.cryptopaylogic.conf_check import check_order_status, HASH_INDEX
from tgbot.cryptopaylogic.database import db_manager
from tgbot.cryptopaylogic.delete_order import delete_sellix_order
from tgbot.yoomoneylogic.check_payment_logic import (
    process_check_payment_and_subscription,
)


def start_periodic_check(
    bot: Bot,
    call,
    chat_id,
    uniqid,
    user_id,
    amount,
    apscheduler: AsyncIOScheduler(timezone="Europe/Moscow"),
):
    job_context = {}
    job_context.setdefault("chat_id", chat_id)
    job_context.setdefault("uniqid", uniqid)

    if not chat_id or not uniqid:
        logging.error("The chat ID or Uniqid is not present in the context of the job.")
        return

    now = datetime.now()

    first_check_time = job_context.get("first_check_time", now)
    job_context["first_check_time"] = first_check_time

    time_diff = now - first_check_time
    delete_after = timedelta(hours=1)

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
                f"Order <code>{uniqid}</code> "
                f"status changed from <code>{last_status}</code> "
                f"to <code>{current_status}</code>"
            )
            bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
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
                bot.send_message(
                    chat_id=chat_id,
                    text=f"Transaction hash: <code>{crypto_hash}</code>",
                    parse_mode="HTML",
                )

        if last_status == "PENDING" and time_diff > delete_after:
            success, message = delete_sellix_order(config.tg_bot.selix_api_key, uniqid)
            if success:
                bot.send_message(
                    chat_id=chat_id,
                    text=f"Order <code>{uniqid}</code> has been automatically cancelled due to timeout.",
                    parse_mode="HTML",
                )
                db_manager.update_order_status(uniqid, "CANCELLED")
                logging.info(
                    f"Order {uniqid} has been automatically cancelled due to timeout, Placed by: {chat_id}"
                )
                job_id = db_manager.get_job_id(uniqid)
                apscheduler.remove_job(job_id)
            else:
                logging.error(
                    f"Failed to automatically cancel order {uniqid}: {message}"
                )

        if current_status == "COMPLETED":
            process_check_payment_and_subscription(call, user_id, amount)
            logging.info(
                f"Order {uniqid} for {amount} successfully executed for {user_id}. Removing the Job"
            )
            job_id = db_manager.get_job_id(uniqid)
            apscheduler.remove_job(job_id)
        elif current_status == "VOIDED":
            logging.info(
                f"Order {uniqid} Was Cancelled, Buyer: {chat_id}. Removing the Job"
            )
            job_id = db_manager.get_job_id(uniqid)
            apscheduler.remove_job(job_id)
    else:
        logging.error(
            f"No current status for order {uniqid}. It might be an API error or network issue."
        )
