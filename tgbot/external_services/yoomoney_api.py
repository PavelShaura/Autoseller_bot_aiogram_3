import uuid as uuid
from dataclasses import dataclass

from yoomoney import Quickpay, Client

from tgbot.config import config


class NoPaymentFound(Exception):
    pass


class NotEnoughMoney(Exception):
    pass


@dataclass
class PaymentYooMoney:
    amount: int
    id: str = None

    def create(self) -> None:
        self.id = str(uuid.uuid4())

    def check_payment(self) -> int:
        client = Client(config.misc.yoomoney_token)
        history = client.operation_history(label=self.id)
        for operation in history.operations:
            return operation.amount
        else:
            raise NoPaymentFound

    @property
    def invoice(self) -> str:
        quickpay = Quickpay(
            receiver=config.misc.yoomoney_wallet,
            quickpay_form="shop",
            targets="Deposit balance",
            paymentType="SB",
            sum=self.amount,
            label=self.id,
        )
        return quickpay.base_url
