import uuid
from dataclasses import dataclass
from yoomoney import Quickpay, Client
from tgbot.config import config


class NoPaymentFound(Exception):
    """
    Exception raised when no payment is found.
    """

    pass


class NotEnoughMoney(Exception):
    """
    Exception raised when there is not enough money.
    """

    pass


@dataclass
class PaymentYooMoney:
    """
    Represents a YooMoney payment.

    Attributes:
        amount (int): The amount of the payment.
        id (str, optional): The ID of the payment.
    """

    amount: int
    id: str = None

    def create(self) -> None:
        """
        Creates a new payment ID.
        """
        self.id = str(uuid.uuid4())

    def check_payment(self) -> int:
        """
        Checks the payment amount.

        Returns:
            int: The amount of the payment.

        Raises:
            NoPaymentFound: If no payment is found.
        """
        client = Client(config.misc.yoomoney_token)
        history = client.operation_history(label=self.id)
        for operation in history.operations:
            return operation.amount
        else:
            raise NoPaymentFound

    @property
    def invoice(self) -> str:
        """
        Generates an invoice for the payment.

        Returns:
            str: The URL of the invoice.
        """
        quickpay = Quickpay(
            receiver=config.misc.yoomoney_wallet,
            quickpay_form="shop",
            targets="Deposit balance",
            paymentType="SB",
            sum=self.amount,
            label=self.id,
        )
        return quickpay.base_url
