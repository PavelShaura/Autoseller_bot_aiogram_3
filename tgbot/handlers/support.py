import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.filters.is_admin import AdminFilter
from tgbot.keyboards.inline import answer_keyboard, cancel_keyboard, support_keyboard
from tgbot.mongo_db.db_api import subs, files, users
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

support_router = Router()


@support_router.message(F.text == "Поддержка")
async def process_support(message: Message):
    await message.answer(text=LEXICON_RU["FAQ"], reply_markup=support_keyboard)


@support_router.callback_query(F.data == "ask_support")
async def ask_support(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=LEXICON_RU["to_ask_support"],
        reply_markup=cancel_keyboard,
    )
    await state.set_state("waiting_question")


@support_router.callback_query(F.data == "cancel")
async def cancel_support(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text=LEXICON_RU["FAQ"], reply_markup=support_keyboard)
    await state.clear()


@support_router.message(StateFilter("waiting_question"))
async def waiting_question(
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
            # Определение словаря с методами отправки сообщений по типу контента
            content_types_methods = {
                ContentType.TEXT: bot.send_message,
                ContentType.PHOTO: bot.send_photo,
                ContentType.VIDEO: bot.send_video,
                ContentType.DOCUMENT: bot.send_document,
            }

            # Определение переменных, которые могут использоваться в различных случаях
            send_args = {
                "chat_id": admin,
                "reply_markup": answer_keyboard(user_id=user_id),
            }

            # Выбор метода отправки сообщения в зависимости от наличия данных о пользователе
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

            # Отправка сообщения с выбранным методом
            await send_method(**send_args)
            logging.info(f"{name} ID:{user_id} -  sent a support request!")

        except Exception as e:
            print(e)
    await message.answer(text=f"<b>✅ Сообщение было отправлено</b>")
    await state.clear()


@support_router.callback_query(F.data.contains("answer"), AdminFilter())
async def process_answer_button(call: CallbackQuery, state: FSMContext):
    data: List[str] = call.data.split(":")
    user_id_to: int = int(data[1])

    await call.message.answer("<b>Отправьте текст для ответа</b>")
    await state.set_state("waiting_answer")

    await state.update_data(user_id_to=user_id_to)


@support_router.message(StateFilter("waiting_answer"), AdminFilter())
async def waiting_answer(message: Message, state: FSMContext):
    data: Dict[str, Any] = await state.get_data()
    user_id_to: int = data.get("user_id_to")
    user = await users.find_one({"_id": user_id_to})
    name = user.get("name")
    await message.copy_to(chat_id=user_id_to)
    await message.answer(text=f"<b>✅ Ответ был отправлен пользователю: {name}</b>")
    await state.clear()


@support_router.callback_query(F.data == "delete", AdminFilter())
async def delete_question(call: CallbackQuery):
    await call.message.delete()
