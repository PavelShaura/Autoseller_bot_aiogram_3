from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить"), KeyboardButton(text="Мои настройки")],
        [KeyboardButton(text="Профиль"), KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="🔥 АКЦИЯ!!! 🔥 ⏱ Пробный период на 3 дня")],
    ],
    resize_keyboard=True,
)

choose_plan_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тариф 3 мес. - 600 руб.")],
        [KeyboardButton(text="Тариф 6 мес. - 900 руб.(скидка 50% 🔥)")],
        [KeyboardButton(text="Тариф 1 год - 1350 руб.(скидка 70% 🔥)")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
