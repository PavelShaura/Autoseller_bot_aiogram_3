from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.filters.is_admin import AdminFilter

waiting_send_answer_to_support_router = Router()


@waiting_send_answer_to_support_router.callback_query(
    F.data.contains("answer"), AdminFilter()
)
async def send_answer_prompt(call: CallbackQuery, state: FSMContext):
    data: List[str] = call.data.split(":")
    user_id_to: int = int(data[1])

    await call.message.answer("<b>Отправьте текст для ответа</b>")
    await state.set_state("waiting_answer")

    await state.update_data(user_id_to=user_id_to)
