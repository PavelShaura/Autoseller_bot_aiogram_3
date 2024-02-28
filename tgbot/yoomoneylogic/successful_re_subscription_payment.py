from datetime import datetime
import os

from aiogram.types import FSInputFile, InlineKeyboardMarkup, CallbackQuery

from tgbot.mongo_db.db_api import files, subs
from tgbot.utils.get_image import get_image_filename
from tgbot.phrasebook.lexicon_ru import LEXICON_RU
from tgbot.config import config

async def process_successful_re_subscription_payment(
    call: CallbackQuery,
    end_date_str: str,
    support_keyboard: InlineKeyboardMarkup,
    settings_keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Processes a successful re-subscription payment.

    Args:
        call (CallbackQuery): The incoming callback query.
        end_date_str (str): The end date of the subscription.
        support_keyboard (InlineKeyboardMarkup): The support keyboard.
        settings_keyboard (InlineKeyboardMarkup): The settings keyboard.

    Returns:
        None
    """
    user_id = call.from_user.id
    date = datetime.now()
    user_data = await files.find_one({"user_id": user_id})

    sub_flag = (
        await subs.find_one(filter={"user_id": user_id, "end_date": {"$gt": date}})
    ).get("client_id", "")

    if len(sub_flag) > 10:
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
                text=LEXICON_RU["empty_qr"], reply_markup=support_keyboard
            )

        image_from_pc = FSInputFile(image_filename)

        result = await call.message.answer_photo(
            photo=image_from_pc,
            caption=f"✅  Оплата прошла успешно!!! \n"
            f"🤝 Ваш QR - код для подключения ⤴️ \n\n"
            f"Cрок действия подписки: до {end_date_str}\n\n"
            f"Меню настроек для подключения ⤵️ ",
            reply_markup=settings_keyboard,
        )
        await files.update_one(
            filter={"user_id": user_id},
            update={"$set": {"photo_id": result.photo[-1].file_id, "pk": pk}},
        )
        await subs.update_one(
            filter={"user_id": user_id, "end_date": {"$gt": date}},
            update={"$set": {"client_id": client_id}},
        )
        os.remove(image_filename)
    else:
        photo_id = user_data.get("photo_id")
        if photo_id:
            await call.message.answer_photo(
                photo=photo_id,
                caption=f"✅  Оплата прошла успешно!!! \n"
                f"Спасибо что Вы снова с нами! 🤝\n"
                f" Ваш QR - код для подключения ⤴️ \n\n"
                f"Общий срок действия подписки: до {end_date_str}\n\n"
                f"Меню настроек для подключения ⤵️ ",
                reply_markup=settings_keyboard,
            )
        else:
            await call.message.answer(
                text=f"✅  Оплата прошла успешно!!! \n"
                f"Спасибо что Вы снова с нами! 🤝\n\n\n"
                f"Общий срок действия подписки: до {end_date_str}\n\n",
                reply_markup=support_keyboard,
            )
