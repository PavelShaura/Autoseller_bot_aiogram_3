from datetime import datetime

from aiogram import Bot

from tgbot.db.db_api import subs
from tgbot.config import config

# Возвращает список пользователей с подпиской
async def get_users_in_subs():
    # Получаем коллекцию с информацией о пользователях и подписках
    users_collection = subs

    # Запрос к базе данных, чтобы выбрать пользователей с информацией о подписках
    # и датой окончания подписки:
    cursor = users_collection.find({"end_date": {"$exists": True}})

    # Преобразуйте результат запроса в список пользователей
    users = await cursor.to_list(length=None)
    return users

async def get_clients_in_subs():
    clients_collection = subs

    cursor = clients_collection.find({"client_id": {"$exists": True}})

    client = await cursor.to_list(length=None)

    return client



# Отправляет оповещение пользователям об окончании подписки
async def send_message_interval(bot: Bot):
    today = datetime.now()
    reminder_days = 2  # За сколько дней оповестить об окончании подписки

    # Получаем список пользователей из базы данных с информацией о подписках и окончании подписки
    users = await get_users_in_subs()

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
    reminder_days = 2  # За сколько дней оповестить об окончании подписки

    clients = await get_clients_in_subs()

    for client in clients:
        end_date = client["end_date"]
        client_id = client["client_id"]

        days_left = (end_date - today).days
        print(days_left)

        if 0 < days_left <= reminder_days:
            message = f"❌ У клиента: {client_id} заканчивается подписка. \n" \
                      f"Остался {days_left} д."
            await bot.send_message(chat_id=config.tg_bot.channel_id, text=message)


# Отправляет оповещение в группу администраторов об успешной оплате подписки
async def send_message_pay(bot: Bot, chat_id: int, amount: int, user, username):
    text = f"📣  Супер! 🔥 Пользователь: {user}({username})👤 оплатил подписку на сумму {amount} 🅿️"
    await bot.send_message(chat_id, text=text)