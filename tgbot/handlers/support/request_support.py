import logging
from datetime import datetime
from typing import Optional

from aiogram import Router, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.config import Config
from tgbot.keyboards.inline import answer_keyboard
from tgbot.mongo_db.db_api import subs, files

request_support_router = Router()


@request_support_router.message(StateFilter("waiting_question"))
async def process_support_request(
    message: Message, state: FSMContext, config: Config, bot: Bot
):
    text: str = message.html_text
    user_id: int = message.from_user.id
    name: str = message.from_user.mention_html()
    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if sub:
        end_date = sub["end_date"].strftime("%d.%m.%Y")
        sub_flag = sub.get("client_id")
        client_id = sub.get("client_id")
        if len(sub_flag) > 10:
            sub_text = (
                "<b>Статус подписки:</b> ⏱ TRIAL ⏱\n"
                f"<b>Срок действия:</b> до {end_date}\n\n"
                f"<b>CLIENT_ID в GUI</b>: {client_id}"
            )
        else:
            sub_text = (
                "<b>Статус подписки:</b> ✅ оплачено ✅\n"
                f"<b>Срок действия:</b> до {end_date}\n\n"
                f"<b>CLIENT_ID в GUI</b>: {client_id}"
            )
    else:
        sub_text = "<b>Статус подписки:</b> ❌ не оплачено ❌\n"

    user_data: dict = await files.find_one({"user_id": user_id})

    photo_id = ""
    if user_data:
        photo_id: str = user_data.get("photo_id")

    text = (
        f"<b>Новый запрос от пользователя ⁉️</b>\n\n"
        f"⬆️ Если пользователю отгружен QR- код, то он прикреплен к запросу\n"
        f"(в случае текстового запроса от пользователя)\n\n"
        f""
        f"<b>ID пользователя:</b> {user_id}\n"
        f"<b>Пользователь:</b> {name}\n\n"
        f"Информация по подписке пользователя {name}:\n\n"
        f"{sub_text}\n\n\n"
        f"<b>Сообщение пользователя:</b>\n"
        f""
        f""
        f"{text}\n\n"
    )

    for admin in config.tg_bot.admin_ids:
        try:
            # Defining a dictionary with methods for sending messages by content type
            content_types_methods = {
                ContentType.TEXT: bot.send_message,
                ContentType.PHOTO: bot.send_photo,
                ContentType.VIDEO: bot.send_video,
                ContentType.DOCUMENT: bot.send_document,
            }

            # Definition of variables that can be used in different cases
            send_args = {
                "chat_id": admin,
                "reply_markup": answer_keyboard(user_id=user_id),
            }

            # Selects the method of sending a message depending on the availability of user data
            send_method = content_types_methods.get(
                message.content_type, bot.send_message
            )
            if user_data:
                if message.content_type == ContentType.TEXT:
                    send_method = bot.send_photo
                    send_args["photo"] = photo_id
                    send_args["caption"] = text
                else:
                    send_method = bot.send_photo
                    send_args["photo"] = message.photo[-1].file_id
                    send_args["caption"] = text
            else:
                send_args["text"] = text

            await send_method(**send_args)
            logging.info(f"{name} ID:{user_id} -  sent a support request!")

        except Exception as e:
            print(e)
    await message.answer(text=f"<b>✅ Сообщение было отправлено</b>")
    await state.clear()
