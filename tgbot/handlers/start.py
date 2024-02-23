import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pymongo.errors import DuplicateKeyError


from tgbot.mongo_db.db_api import users
from tgbot.phrasebook.lexicon_ru import LEXICON_RU
from tgbot.keyboards.inline import choose_payment

from tgbot.keyboards.reply import menu_keyboard, choose_plan_keyboard


start_router = Router()


@start_router.message(CommandStart(), flags={"throttling_key": "default"})
async def user_start(message: Message):
    await message.answer(text=LEXICON_RU["menu"], reply_markup=menu_keyboard)
    _id: int = message.from_user.id
    name: str = message.from_user.full_name
    username: str = message.from_user.username
    try:
        await users.insert_one(
            {
                "_id": message.from_user.id,
                "name": name,
                "username": username,
                "date": message.date,
            }
        )
        logging.info(f"{name} {username} came to see us!")
    except DuplicateKeyError:
        pass


@start_router.message(F.text == "Оплатить")
async def choose_pay_method(query: Message):
    await query.answer(text="Выберите тариф! ⤵️", reply_markup=choose_plan_keyboard)


@start_router.message(
    F.text.in_(
        {
            "Тариф 1 год - 1350 руб.(скидка 70% 🔥)",
            "Тариф 3 мес. - 600 руб.",
            "Тариф 6 мес. - 900 руб.(скидка 50% 🔥)",
        }
    ),
)
async def choose_plan(query: Message, state: FSMContext):
    data = query.text.split()

    current_price = data[4]
    month = data[1] + data[2]

    await query.answer(text="Выберите способ оплаты", reply_markup=choose_payment)
    await state.set_state("check_plan")
    await state.update_data(current_price=current_price, month=month)
