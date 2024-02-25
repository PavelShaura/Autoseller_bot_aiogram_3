import logging
import aiohttp
from typing import Tuple


async def delete_sellix_order(api_key: str, uniqid: str) -> Tuple[bool, str]:
    """
    Delete a Sellix order.

    Args:
        api_key (str): The API key for authentication.
        uniqid (str): The unique identifier of the order.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success and a message.

    This function sends a request to delete a Sellix order using the provided API key and order ID.
    """
    url: str = f"https://dev.sellix.io/v1/payments/{uniqid}"
    headers: dict = {"Authorization": f"Bearer {api_key}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(url, headers=headers) as response:
                if response.status == 200:
                    logging.info(f"Order {uniqid} has been successfully deleted.")
                    return True, f"Заказ {uniqid} был успешно удален."
                else:
                    logging.error(f"Failed to delete order {uniqid}: {response.text}")
                    return False, f"Не удалось удалить заказ {uniqid}: {response.text}"
        except aiohttp.ClientError as e:
            logging.error(f"Failed to delete order {uniqid}: {e}")
            return False, f"Не удалось удалить заказ {uniqid}: {e}"
