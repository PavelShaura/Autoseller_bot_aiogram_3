from datetime import datetime
from typing import Optional
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from pymongo.errors import OperationFailure

from tgbot.keyboards.inline import show_qr_keyboard, support_keyboard
from tgbot.keyboards.reply import menu_keyboard
from tgbot.mongo_db.db_api import subs, files, trial
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

os_selection_settings_router = Router()


@os_selection_settings_router.callback_query(
    F.data.contains("choose_os"), flags={"throttling_key": "callback"}
)
async def process_os_selection_settings(call: CallbackQuery):
    user_id: int = call.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )

    if not sub:
        await call.answer(text=LEXICON_RU["not_sub"], show_alert=True)

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
