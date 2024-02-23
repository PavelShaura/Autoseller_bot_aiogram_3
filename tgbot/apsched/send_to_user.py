import logging
from datetime import datetime

from aiogram import Bot

from tgbot.mongo_db.get_data_in_mongodb import get_data_in_subs


# Отправляет оповещение пользователям об окончании подписки
async def notification_to_user(bot: Bot):
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
            logging.info(f"Subscription expiry notice sent for {user}")
