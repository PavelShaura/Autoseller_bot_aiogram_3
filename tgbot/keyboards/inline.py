from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_support")]
    ]
)


def answer_keyboard(user_id):
    answer_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💬 Ответить", callback_data=f"answer:{user_id}"
                ),
                InlineKeyboardButton(text=f"❎ Удалить", callback_data=f"delete"),
            ],
        ]
    )
    return answer_markup


def payment_keyboard(payment_id: str, invoice: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=invoice)],
            [
                InlineKeyboardButton(
                    text="ПРОВЕРИТЬ ПЛАТЕЖ",
                    callback_data=f"check_payment:{payment_id}",
                )
            ],
            [InlineKeyboardButton(text="Назад в меню", callback_data="to_menu")]
        ]
    )

    return keyboard


cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel")]]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Продлить подписку", callback_data="prolong")]
    ]
)

os_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Iphone", callback_data="choose_os:iphone"),
            InlineKeyboardButton(text="Android", callback_data="choose_os:android"),
        ],
        [
            InlineKeyboardButton(text="MacOS", callback_data="choose_os:macos"),
            InlineKeyboardButton(text="Windows", callback_data="choose_os:windows"),
        ],
    ]
)

settings_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Настроить", callback_data="settings")]]
)

show_qr_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Показать Ваш QR-код", callback_data="show_qr")]
    ]
)

choose_payment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Банковская карта 💳", callback_data="u_money"),
            InlineKeyboardButton(text="BITCOIN 💸", callback_data="cryptopay"),
        ]
    ]
)

status_or_cancel_payment_bitcoin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Проверить статус платежа", callback_data="btc_status"
            ),
            InlineKeyboardButton(text="Отменить платеж", callback_data="btc_cancel"),
        ]
    ]
)

back_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="to_menu")]
    ]
)
