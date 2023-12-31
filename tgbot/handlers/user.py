from datetime import datetime
from typing import Union, Optional

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pymongo.errors import DuplicateKeyError

from tgbot.db.db_api import users, subs
from tgbot.lexicon.lexicon_ru import LEXICON_RU
from tgbot.external_services.yoomoney_api import PaymentYooMoney
from tgbot.keyboards.inline import (
    support_keyboard,
    payment_keyboard,
    os_keyboard,
    show_qr_keyboard,
)
from tgbot.keyboards.reply import menu_keyboard, choose_plan_keyboard

user_router = Router()


@user_router.message(CommandStart(), flags={"throttling_key": "default"})
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
    except DuplicateKeyError:
        pass


@user_router.message(F.text == "Оплатить")
async def choose_plan(query: Message):
    await query.answer(text="Выберите тариф! ⤵️ ", reply_markup=choose_plan_keyboard)


@user_router.message(
    F.text.in_(
        {
            "Тариф 1 год - 1350 руб.(скидка 70% 🔥)",
            "Тариф 3 мес. - 600 руб.",
            "Тариф 6 мес. - 900 руб.(скидка 50% 🔥)",
        }
    ),
    flags={"throttling_key": "payment"},
)
async def process_pay(query: Union[Message, CallbackQuery], state: FSMContext):
    user_id: int = query.from_user.id
    date: datetime = datetime.now()

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": date}}
    )
    sub_text = ""
    if sub:
        sub_text = "\n\n<i> ✅ У вас уже активирована подписка. При оплате подписка будет продлена. </i> \n\n"

    sub_name = query.text.split()

    current_price = sub_name[4]
    price_list = ["600", "900", "1350"]

    if current_price in price_list:
        amount = int(current_price)
        text = (
            f"Оплата\n\n\n"
            f"Цена за {sub_name[1]} {sub_name[2]}: {amount} руб. {sub_text}\n"
            f"Оплата банковской картой через платежную систему ЮМани.\n"
            f"Это надёжно и удобно."
        )

        payment = PaymentYooMoney(amount=amount)
        payment.create()

        try:
            if isinstance(query, Message):
                await query.answer(
                    text=text,
                    reply_markup=payment_keyboard(
                        payment_id=payment.id, invoice=payment.invoice
                    ),
                )
            else:
                await query.message.edit_text(
                    text=text,
                    reply_markup=payment_keyboard(
                        payment_id=payment.id, invoice=payment.invoice
                    ),
                )
        except TelegramBadRequest:
            pass

        await state.set_state("check_payment")
        await state.update_data(payment_id=payment.id, amount=payment.amount)
    else:
        await query.message.answer(
            text="Извините, данный тариф недействителен. Выберите другой тариф  ⤵️",
            reply_markup=choose_plan_keyboard)


@user_router.callback_query(F.data == "settings")
@user_router.message(F.text == "Мои настройки")
async def process_settings(query: Union[Message, CallbackQuery]):
    user_id: int = query.from_user.id

    message: Message = query if isinstance(query, Message) else query.message

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if not sub:
        await message.answer(text=LEXICON_RU["no_sub"])
        return

    await message.answer(
        text=LEXICON_RU["yes_sub"],
        disable_web_page_preview=True,
        reply_markup=os_keyboard,
    )


@user_router.message(F.text == "Профиль")
async def process_profile(message: Message):
    user_id: int = message.from_user.id
    name: str = message.from_user.first_name
    username: str = (
        f"<b>Юзернейм:</b> {message.from_user.username}\n"
        if message.from_user.username
        else ""
    )

    sub: Optional[dict] = await subs.find_one(
        filter={"user_id": user_id, "end_date": {"$gt": datetime.now()}}
    )

    if sub:
        end_date: str = sub["end_date"].strftime("%d.%m.%Y")
        sub_text: str = f"Статус подписки: ✅ активирована\nСрок действия: до {end_date}"
        reply_markup = show_qr_keyboard
    else:
        sub_text = "Статус подписки: ❌ не активирована"
        reply_markup = choose_plan_keyboard

    text = f"Профиль\n\nВаш ID: {user_id}\nИмя: {name}\n{username}\n\n{sub_text}\n"

    await message.answer(text=text, reply_markup=reply_markup)


@user_router.message(F.text == "Поддержка")
async def process_support(message: Message):
    await message.answer(text=LEXICON_RU["FAQ"], reply_markup=support_keyboard)
