from datetime import datetime
import os

from aiogram.types import FSInputFile, InlineKeyboardMarkup, CallbackQuery

from tgbot.mongo_db.db_api import files, subs
from tgbot.utils.get_image import get_image_filename
from tgbot.phrasebook.lexicon_ru import LEXICON_RU
from tgbot.config import config

async def process_successful_first_subscription_payment(
    call: CallbackQuery,
    end_date_str: str,
    support_keyboard: InlineKeyboardMarkup,
    settings_keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Processes a successful first subscription payment.

    Args:
        call (CallbackQuery): The incoming callback query..
        end_date_str (str): The end date of the subscription.
        support_keyboard (InlineKeyboardMarkup): The support keyboard.
        settings_keyboard (InlineKeyboardMarkup): The settings keyboard.

    Returns:
        None
    """
    user_id = call.from_user.id
    date: datetime = datetime.now()

    image_filename = ""
    client_id = ""
    pk = ""

    async for image in get_image_filename(config.tg_bot.sub_image_folder):
        image_filename = image
        break
    try:
        pk = image_filename.split("/")[3].split(".")[0]
        client_id = "Client_№" + pk
    except Exception as e:
        print(e)
    if not os.path.exists(image_filename):
        await call.message.answer(
            text=LEXICON_RU["empty_qr"],
            reply_markup=support_keyboard,
        )

    image_from_pc = FSInputFile(image_filename)

    result = await call.message.answer_photo(
        photo=image_from_pc,
        caption=f"✅  Оплата прошла успешно!!! \n\n\n"
        f"Ваш QR - код для подключения ⤴️ \n\n"
        f"<b>Срок действия:</b> до {end_date_str}\n\n"
        f"Перейдите в меню настроек для подключения",
        reply_markup=settings_keyboard,
    )

    await files.insert_one(
        {"user_id": user_id, "photo_id": result.photo[-1].file_id, "pk": pk}
    )
    await subs.update_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}},
        update={"$set": {"client_id": client_id}},
    )
    os.remove(image_filename)
