import logging
import requests


async def delete_sellix_order(api_key, uniqid):
    url = f"https://dev.sellix.io/v1/payments/{uniqid}"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"Order {uniqid} has been successfully deleted.")
        return True, f"Заказ {uniqid} был успешно удален."

    else:
        logging.error(f"Failed to delete order {uniqid}: {response.text}")
        return False, f"Не удалось удалить заказ {uniqid}: {response.text}"
