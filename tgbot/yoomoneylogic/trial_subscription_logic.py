from datetime import datetime, timedelta
import os
from typing import Union

from aiogram.types import FSInputFile, InlineKeyboardMarkup, CallbackQuery, Message

from tgbot.mongo_db.db_api import files, subs, trial


async def process_trial_subscription(
    query: Union[Message, CallbackQuery],
    settings_keyboard: InlineKeyboardMarkup,
    client_id: str,
    image_filename: str,
    pk: str,
) -> None:
    """
    Processes a trial subscription.

    Args:
        query (Union[Message, CallbackQuery]): The query object representing the message.
        settings_keyboard (InlineKeyboardMarkup): The settings keyboard.
        client_id (str): The client ID.
        image_filename (str): The image filename.
        pk (str): The package ID.

    Returns:
        None
    """
    user_id: int = query.from_user.id
    date: datetime = datetime.now()

    await subs.delete_many(filter={"user_id": user_id})

    end_date = date + timedelta(days=3)

    await trial.insert_one(
        {
            "user_id": user_id,
            "trial_flag": "on",
            "start_date": date,
            "end_date": end_date,
        }
    )

    await subs.insert_one(
        document={
            "user_id": user_id,
            "start_date": date,
            "end_date": end_date,
            "client_id": client_id,
        }
    )

    image_from_pc = FSInputFile(image_filename)

    end_date_str: str = end_date.strftime("%d.%m.%Y")

    result = await query.answer_photo(
        photo=image_from_pc,
        caption=f"✅  Подписка успешно оформлена!!! \n\n\n"
        f"Ваш QR - код для подключения ⤴️ \n\n"
        f"<b>Срок действия пробного периода:</b> до {end_date_str}\n\n"
        f"Перейдите в меню настроек для подключения",
        reply_markup=settings_keyboard,
    )

    await files.insert_one(
        {"user_id": user_id, "photo_id": result.photo[-1].file_id, "pk": pk}
    )

    os.remove(image_filename)
