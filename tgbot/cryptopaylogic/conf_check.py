import requests


UNIQID_INDEX = 0
CHAT_ID_INDEX = 1
USER_ID_INDEX = 2
USERNAME_INDEX = 3
STATUS_INDEX = 4
CRYPTO_INDEX = 5
AMOUNT_INDEX = 6
PLAN_INDEX = 7
HASH_INDEX = 8


async def check_order_status(api_key, uniqid):
    url = f"https://dev.sellix.io/v1/orders/{uniqid}"
    headers = {"Authorization": f"Bearer {api_key}"}
    status, crypto_hash = None, None

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Non-successful response code: {response.status_code}")
            return status, crypto_hash

        # Проверяем что ответ содержит корректный JSON
        response_json = response.json()
        if not isinstance(response_json, dict):
            print(f"Invalid JSON response: {response_json}")
            return status, crypto_hash

        # Извлечение деталей заказа
        order_details = response_json.get("data", {}).get("order", {})
        if not isinstance(order_details, dict):
            print(f"Invalid order details format: {order_details}")
            return status, crypto_hash

        # Извлечение status и crypto_hash
        status = order_details.get("status")
        if status in ["WAITING_FOR_CONFIRMATIONS", "COMPLETED"]:
            transactions = order_details.get("crypto_transactions", [])
            if transactions and isinstance(transactions, list):
                crypto_hash = transactions[0].get("hash")

    except requests.RequestException as e:
        print(f"Failed to get order status: {e}")

    return status, crypto_hash
