from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import cancel_keyboard

from tgbot.phrasebook.lexicon_ru import LEXICON_RU

ask_support_router = Router()


@ask_support_router.callback_query(F.data == "ask_support")
async def ask_support(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=LEXICON_RU["to_ask_support"],
        reply_markup=cancel_keyboard,
    )
    await state.set_state("waiting_question")
