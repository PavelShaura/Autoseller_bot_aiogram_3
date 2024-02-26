from tgbot.handlers.payments.Invoice_payment_bitcoin import payment_bitcoin_router
from tgbot.handlers.payments.cancel_payment_btc import cancel_payment_btc_router
from tgbot.handlers.payments.check_payment_btc import check_payment_btc_router
from tgbot.handlers.payments.check_payment_u_money import check_payment_u_money_router
from tgbot.handlers.payments.ivoice_payment_umoney import payment_u_money_router
from tgbot.handlers.profile.profile_user import profile_user_router
from tgbot.handlers.settings.process_os_selection import os_selection_settings_router
from tgbot.handlers.settings.show_qr_settings import show_qr_router
from tgbot.handlers.settings.user_settings import user_settings_router
from tgbot.handlers.start.choose_pay_method import choose_pay_method_router
from tgbot.handlers.start.choose_plan_subscription import (
    choose_plan_subscription_router,
)
from tgbot.handlers.start.command_start import command_start_router
from tgbot.handlers.support.ask_support_question import ask_support_router
from tgbot.handlers.support.cancel_support import cancel_support_router
from tgbot.handlers.support.request_support import request_support_router
from tgbot.handlers.support.send_or_delete_answer_to_user import (
    send_answer_support_router,
)
from tgbot.handlers.support.show_faq_support import show_faq_support_router
from tgbot.handlers.support.waiting_send_answer import (
    waiting_send_answer_to_support_router,
)
from tgbot.handlers.trial.trial_subscription import trial_subscription_router

routers = [
    trial_subscription_router,
    waiting_send_answer_to_support_router,
    show_faq_support_router,
    send_answer_support_router,
    request_support_router,
    cancel_support_router,
    ask_support_router,
    command_start_router,
    choose_plan_subscription_router,
    choose_pay_method_router,
    user_settings_router,
    show_qr_router,
    os_selection_settings_router,
    profile_user_router,
    payment_u_money_router,
    check_payment_u_money_router,
    check_payment_btc_router,
    cancel_payment_btc_router,
    payment_bitcoin_router,
]
