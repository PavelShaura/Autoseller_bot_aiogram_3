from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.keyboards.inline import choose_payment

choose_pay_method_router = Router()


@choose_pay_method_router.message(
    F.text.in_(
        {
            "Тариф 1 год - 1350 руб.(скидка 70% 🔥)",
            "Тариф 3 мес. - 600 руб.",
            "Тариф 6 мес. - 900 руб.(скидка 50% 🔥)",
        }
    ),
)
async def choose_how_to_pay(query: Message, state: FSMContext) -> None:
    """
    Handles the message with text corresponding to a subscription plan.

    Args:
        query (Message): The incoming message.
        state (FSMContext): The FSMContext object.

    Returns:
        None
    """
    data = query.text.split()

    current_price = data[4]
    month = data[1] + data[2]

    await query.answer(text="Выберите способ оплаты", reply_markup=choose_payment)
    await state.set_state("check_plan")
    await state.update_data(current_price=current_price, month=month)
