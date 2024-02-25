import logging
import aiohttp


async def delete_sellix_order(api_key, uniqid):
    url = f"https://dev.sellix.io/v1/payments/{uniqid}"
    headers = {"Authorization": f"Bearer {api_key}"}

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
