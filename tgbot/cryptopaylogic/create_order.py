import aiohttp
import logging
from typing import Tuple


async def create_order(
    api_key: str, gateway: str, value: float
) -> Tuple[str, str, str, str, float]:
    """
    Create an order.

    Args:
        api_key (str): The API key for authentication.
        gateway (str): The payment gateway (in this bot used BITCOIN)
        value (float): The value of the order.

    Returns:
        Tuple[str, str, str, str, float]: A tuple containing the address, amount, uniqid, protocol, and value.

    This function creates a payment order using the Sellix API.
    """
    endpoint: str = "https://dev.sellix.io/v1/payments"
    payload: dict = {
        "title": "License Key",
        "value": value,
        "currency": "RUB",
        "quantity": 1,
        "email": "gkdrdfffe@gmail.com",
        "gateway": gateway,
        "white_label": True,
        "confirmations": 1,
    }
    headers: dict = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=payload, headers=headers) as response:
            if response.status != 200:
                logging.info(
                    f"Failed to create payment. Status Code: {response.status}, Response: {await response.text()}"
                )
                raise Exception(
                    f"Failed to create payment. Status Code: {response.status}, Response: {await response.text()}"
                )

            data: dict = await response.json()
            invoice: dict = data.get("data", {}).get("invoice", {})
            if not (invoice and isinstance(invoice, dict)):
                logging.info(f"Unexpected response structure: {data}")
                raise Exception("Unexpected data structure in response.")

            crypto_uri: str = invoice.get("crypto_uri")
            uniqid: str = invoice.get("uniqid")
            if not (crypto_uri and uniqid):
                logging.info(f"crypto_uri or uniqid is missing: {invoice}")
                raise Exception("Missing crypto_uri or uniqid in the response.")

            try:
                address, amount_param = crypto_uri.split("?")
                if ":" in address:
                    protocol, address = address.split(":", 1)
                amount: str = amount_param.split("=")[1]
                return address, amount, uniqid, protocol, value
            except Exception as e:
                logging.info(f"Error splitting crypto_uri: {crypto_uri}")
                raise Exception(f"Error processing crypto_uri: {e}")
