from aiogram import Router, F
from aiogram.types import Message

from tgbot.keyboards.inline import support_keyboard
from tgbot.phrasebook.lexicon_ru import LEXICON_RU

show_faq_support_router = Router()


@show_faq_support_router.message(F.text == "Поддержка")
async def show_support(message: Message):
    await message.answer(text=LEXICON_RU["FAQ"], reply_markup=support_keyboard)
