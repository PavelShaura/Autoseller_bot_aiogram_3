import logging
from datetime import datetime
from typing import Any

from aiogram import Bot

from tgbot.keyboards.inline import profile_keyboard
from tgbot.mongo_db.get_data_in_mongodb import get_data_in_subs


async def notification_to_user(bot: Bot) -> None:
    """
    Send subscription expiration notifications to users.

    Args:
        bot (Bot): The bot instance to send notifications.

    Returns:
        None

    This function sends notifications to users about the expiration of their subscriptions.
    It retrieves user data from the database with subscription information and expiration dates.
    If the subscription is ending within the reminder days, it sends a notification to the user.
    """
    today: datetime = datetime.now()
    reminder_days: int = (
        2  # How many days before subscription expiry to send a reminder
    )

    users: Any = await get_data_in_subs({"end_date": {"$exists": True}})

    for user in users:
        user_id: int = user["user_id"]
        end_date: datetime = user["end_date"]

        days_left: int = (end_date - today).days

        if 0 < days_left <= reminder_days:
            message: str = f"Ваша подписка закончится через {days_left} д."
            await bot.send_message(
                chat_id=user_id, text=message, reply_markup=profile_keyboard
            )
            logging.info(f"Subscription expiry notice sent for user: {user_id}")
