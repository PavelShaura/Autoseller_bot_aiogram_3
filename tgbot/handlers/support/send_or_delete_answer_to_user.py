from typing import Dict, Any

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.filters.is_admin import AdminFilter
from tgbot.mongo_db.db_api import users

send_answer_support_router = Router()


@send_answer_support_router.message(StateFilter("waiting_answer"), AdminFilter())
async def send_answer(message: Message, state: FSMContext):
    data: Dict[str, Any] = await state.get_data()
    user_id_to: int = data.get("user_id_to")
    user = await users.find_one({"_id": user_id_to})
    name = user.get("name")
    await message.copy_to(chat_id=user_id_to)
    await message.answer(text=f"<b>✅ Ответ был отправлен пользователю: {name}</b>")
    await state.clear()


@send_answer_support_router.callback_query(F.data == "delete", AdminFilter())
async def delete_question(call: CallbackQuery):
    await call.message.delete()
