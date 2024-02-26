from typing import Union

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.reply import choose_plan_keyboard

choose_plan_subscription_router = Router()


@choose_plan_subscription_router.callback_query(F.data == "prolong")
@choose_plan_subscription_router.message(F.text == "Оплатить")
async def choose_pay_method(query: Union[Message, CallbackQuery]) -> None:
    """
    Handles the callback query "prolong" or message with text "Оплатить".

    Args:
        query (Union[Message, CallbackQuery]): The incoming message or callback query.

    Returns:
        None
    """
    message: Message = query if isinstance(query, Message) else query.message
    await message.answer(text="Выберите тариф! ⤵️", reply_markup=choose_plan_keyboard)
