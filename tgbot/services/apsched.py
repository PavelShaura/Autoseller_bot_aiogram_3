from datetime import datetime

from aiogram import Bot

from tgbot.db.db_api import subs
from tgbot.config import config


async def get_data_in_subs(filter_criteria):
    collection = subs
    cursor = collection.find(filter_criteria)
    data = await cursor.to_list(length=None)
    return data


# Отправляет оповещение пользователям об окончании подписки
async def send_message_interval(bot: Bot):
    today = datetime.now()
    reminder_days = 2  # За сколько дней оповестить об окончании подписки

    # Получаем список пользователей из базы данных с информацией о подписках и окончании подписки
    users = await get_data_in_subs({"end_date": {"$exists": True}})

    for user in users:
        user_id = user["user_id"]
        end_date = user["end_date"]

        # Рассчитываем, сколько дней осталось до окончания подписки
        days_left = (end_date - today).days

        if 0 < days_left <= reminder_days:
            message = f"Ваша подписка закончится через {days_left} д."
            await bot.send_message(chat_id=user_id, text=message)


# Отправляет оповещение c ID клиента в группу администраторов об окончании подписки
async def send_admin_end_date(bot: Bot):
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


# Отправляет оповещение в группу администраторов об успешной оплате подписки
async def send_message_pay(bot: Bot, chat_id: int, amount: int, user, username):
    text = f"📣  Супер! 🔥 Пользователь: {user}({username})👤 оплатил подписку на сумму {amount} 🅿️"
    await bot.send_message(chat_id, text=text)


async def send_message_trial(bot: Bot, chat_id: int, user, username, client_id):
    text = (
        f"⏱ Пользователь: {user}({username})👤 оформил TRIAL(пробный период)\n"
        f"client_id: {client_id}"
    )
    await bot.send_message(chat_id, text=text)
