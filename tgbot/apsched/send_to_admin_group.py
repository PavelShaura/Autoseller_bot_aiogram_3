import logging
from datetime import datetime

from aiogram import Bot

from tgbot.config import config
from tgbot.mongo_db.get_data_in_mongodb import get_data_in_subs


async def notification_to_admin_group(bot: Bot):
    today = datetime.now()
    reminder_days = 1  # За сколько дней оповестить об окончании подписки

    clients = await get_data_in_subs({"client_id": {"$exists": True}})

    for client in clients:
        end_date = client["end_date"]
        client_id = client["client_id"]

        days_left = (end_date - today).days
        print(days_left)

        if 0 < days_left <= reminder_days:
            message = (
                f"❌ У клиента: {client_id} заканчивается подписка. \n"
                f"Остался {days_left} д."
            )
            await bot.send_message(chat_id=config.tg_bot.channel_id, text=message)
            logging.info(
                f"Client: {client_id} is running out of subscriptions. Days left: {days_left} "
            )


async def notification_payment_cleared(
    bot: Bot, chat_id: int, amount: int, user, username
):
    text = f"📣  Супер! 🔥 Пользователь: {user}({username})👤 оплатил подписку на сумму {amount} 🅿️"
    await bot.send_message(chat_id, text=text)
    logging.info(
        f"User: {user}({username}) has paid a subscription for the amount of {amount}"
    )


async def notification_trial_taken(bot: Bot, chat_id: int, user, username, client_id):
    text = (
        f"⏱ Пользователь: {user}({username})👤 оформил TRIAL(пробный период)\n"
        f"client_id: {client_id}"
    )
    await bot.send_message(chat_id, text=text)
    logging.info(
        f"User: {user}({username})👤 has signed up for a TRIAL(trial period) ID: {client_id}"
    )
