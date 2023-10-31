from datetime import datetime

from aiogram import Bot

from tgbot.db.db_api import subs


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


# Отправляет оповещение пользователям об окончании подписки
async def send_message_interval(bot: Bot):
    today = datetime.now()
    reminder_days = 3  # За сколько дней оповестить об окончании подписки

    # Получаем список пользователей из базы данных с информацией о подписках и окончании подписки
    users = await get_users_in_subs()

    for user in users:
        user_id = user["user_id"]
        end_date = user["end_date"]

        # Рассчитываем, сколько дней осталось до окончания подписки
        days_left = (end_date - today).days

        if 0 < days_left <= reminder_days:
            message = f"Ваша подписка закончится через {days_left} дня."
            await bot.send_message(chat_id=user_id, text=message)
