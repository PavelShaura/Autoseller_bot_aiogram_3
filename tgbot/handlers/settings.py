from datetime import datetime
from typing import Optional
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from tgbot.db.db_api import subs, files
from tgbot.keyboards.inline import show_qr_keyboard, support_keyboard
from tgbot.keyboards.reply import menu_keyboard
from tgbot.lexicon.lexicon_ru import LEXICON_RU

settings_router = Router()


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
        await call.message.edit_text(
            text=LEXICON_RU["mobile_support"],
            reply_markup=show_qr_keyboard,
        )
    elif _os in ["macos", "windows"]:

        user_data: dict = await files.find_one({"user_id": user_id})
        pk: str = user_data.get("pk")

        file_path = f"tgbot/client_conf_files/{pk}.conf"

        if not os.path.exists(file_path):
            await call.message.answer(
                text="Файл не найден, обратитесь к администратору",
                reply_markup=support_keyboard,
            )
            return

        file_from_pc: FSInputFile = FSInputFile(file_path)

        conf_result = await call.message.answer_document(
            document=file_from_pc,
            caption="Фаш файл конфигурации",
            reply_markup=menu_keyboard)

        await files.update_one(
            filter={"user_id": user_id},
            update={"$set": {"file_id": conf_result.document.file_id}},
        )




@settings_router.callback_query(F.data.contains("show_qr"))
async def show_qr(call: CallbackQuery):
    user_id: int = call.from_user.id
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
