from yoomoney import Authorize
from tgbot.config import config


# Docs: https://github.com/AlekseyKorshuk/yoomoney-api

Authorize(
    client_id=config.misc.client_id,
    redirect_uri=config.misc.redirect_url,
    scope=[
        "account-info",
        "operation-history",
        "operation-details",
        "incoming-transfers",
        "payment-p2p",
        "payment-shop",
    ],
)
