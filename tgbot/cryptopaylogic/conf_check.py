import aiohttp
from typing import Tuple, Optional

UNIQID_INDEX = 0
CHAT_ID_INDEX = 1
USER_ID_INDEX = 2
USERNAME_INDEX = 3
STATUS_INDEX = 4
CRYPTO_INDEX = 5
AMOUNT_INDEX = 6
PLAN_INDEX = 7
HASH_INDEX = 8


async def check_order_status(
    api_key: str, uniqid: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Check the status of an order.

    Args:
        api_key (str): The API key for authentication.
        uniqid (str): The unique identifier of the order.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the status and crypto hash of the order.

    This function sends a request to the Sellix API to check the status of a specific order.
    It retrieves the order status and crypto hash if the order is in 'WAITING_FOR_CONFIRMATIONS' or 'COMPLETED' status.
    """
    url: str = f"https://dev.sellix.io/v1/orders/{uniqid}"
    headers: dict = {"Authorization": f"Bearer {api_key}"}
    status: Optional[str] = None
    crypto_hash: Optional[str] = None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Non-successful response code: {response.status}")
                    return status, crypto_hash

                response_json: dict = await response.json()
                order_details: dict = response_json.get("data", {}).get("order", {})
                status = order_details.get("status")

                if status in ["WAITING_FOR_CONFIRMATIONS", "COMPLETED"]:
                    transactions: list = order_details.get("crypto_transactions", [])
                    if transactions and isinstance(transactions, list):
                        crypto_hash = transactions[0].get("hash")
        except aiohttp.ClientError as e:
            print(f"Failed to get order status: {e}")

    return status, crypto_hash
