import logging
from datetime import datetime
from typing import Optional, Union
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from pymongo.errors import OperationFailure


from tgbot.keyboards.inline import show_qr_keyboard, support_keyboard, os_keyboard
from tgbot.keyboards.reply import menu_keyboard
from tgbot.mongo_db.db_api import subs, files, trial
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

settings_router = Router()


@settings_router.callback_query(F.data == "settings")
@settings_router.message(F.text == "Мои настройки")
async def process_settings(query: Union[Message, CallbackQuery]):
    user_id: int = query.from_user.id

    message: Message = query if isinstance(query, Message) else query.message

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if not sub:
        await message.answer(text=LEXICON_RU["no_sub"])
        return

    await message.answer(
        text=LEXICON_RU["yes_sub"],
        disable_web_page_preview=True,
        reply_markup=os_keyboard,
    )


@settings_router.callback_query(
    F.data.contains("choose_os"), flags={"throttling_key": "callback"}
)
async def choose_os(call: CallbackQuery):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)
        return

    data: list[str] = call.data.split(":")
    _os: str = data[1]
    if _os in ["iphone", "android"]:
        if _os == "iphone":
            await call.message.edit_text(
                text=LEXICON_RU["iphone_support"],
                disable_web_page_preview=True,
                reply_markup=show_qr_keyboard,
            )
        if _os == "android":
            await call.message.edit_text(
                text=LEXICON_RU["android_support"],
                disable_web_page_preview=True,
                reply_markup=show_qr_keyboard,
            )
    elif _os in ["macos", "windows"]:
        global file_path
        file_path = ""

        user_data: dict = await files.find_one({"user_id": user_id})
        trials: dict = await trial.find_one(filter={"user_id": user_id})

        if trials:
            trial_flag = trials.get("trial_flag")

            if trial_flag == "on":
                pk: str = user_data.get("pk")
                file_path = f"tgbot/static_files/trial_conf_file/{pk}.conf"
            else:
                pk: str = user_data.get("pk")
                file_path = f"tgbot/static_files/client_conf_files/{pk}.conf"
        else:
            pk: str = user_data.get("pk")
            file_path = f"tgbot/static_files/client_conf_files/{pk}.conf"
        print(file_path)
        if not os.path.exists(file_path):
            try:
                file_id = user_data.get("file_id")
                if _os == "macos":
                    await call.message.answer_document(
                        document=file_id,
                        caption=LEXICON_RU["macos_support"],
                        disable_web_page_preview=True,
                        reply_markup=menu_keyboard,
                    )
                elif _os == "windows":
                    await call.message.answer_document(
                        document=file_id,
                        caption=LEXICON_RU["windows_support"],
                        disable_web_page_preview=True,
                        reply_markup=menu_keyboard,
                    )
                else:
                    await call.message.answer(
                        text="Файл не найден, обратитесь к администратору",
                        reply_markup=support_keyboard,
                    )
                    return
            except Exception as e:
                print(e)
        else:
            file_from_pc: FSInputFile = FSInputFile(file_path)

            conf_result = ""
            print(file_path)
            if _os == "macos":
                conf_result = await call.message.answer_document(
                    document=file_from_pc,
                    caption=LEXICON_RU["macos_support"],
                    disable_web_page_preview=True,
                    reply_markup=menu_keyboard,
                )

            if _os == "windows":
                conf_result = await call.message.answer_document(
                    document=file_from_pc,
                    caption=LEXICON_RU["windows_support"],
                    disable_web_page_preview=True,
                    reply_markup=menu_keyboard,
                )
            try:
                await files.update_one(
                    filter={"user_id": user_id},
                    update={"$set": {"file_id": conf_result.document.file_id}},
                )
            except OperationFailure:
                await files.insert_one(
                    {"user_id": user_id, "file_id": conf_result.document.file_id}
                )
            os.remove(file_path)


@settings_router.callback_query(F.data.contains("show_qr"))
async def show_qr(call: CallbackQuery):
    user_id: int = call.from_user.id
    username = call.from_user.username
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    user_data: Optional[dict] = await files.find_one({"user_id": user_id})

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)
        return
    else:
        if user_data:
            photo_id: str = user_data.get("photo_id")

            await call.message.answer_photo(
                photo=photo_id, caption=f"Ваш QR-код для подключения ⤴️"
            )
        else:
            await call.message.answer(
                text=LEXICON_RU["empty_qr"],
                reply_markup=support_keyboard,
            )
            logging.info(f"For {user_id} {username} QR- code didn't send")
