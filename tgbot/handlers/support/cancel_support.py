from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import support_keyboard
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

cancel_support_router = Router()


@cancel_support_router.callback_query(F.data == "cancel")
async def cancel_support(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text=LEXICON_RU["FAQ"], reply_markup=support_keyboard)
    await state.clear()
