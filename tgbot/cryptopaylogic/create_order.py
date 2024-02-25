import logging

import requests


async def create_order(api_key, gateway, value):
    endpoint = "https://dev.sellix.io/v1/payments"
    payload = {
        "title": "License Key",
        "value": value,
        "currency": "RUB",
        "quantity": 1,
        "email": "gkdrdfffe@gmail.com",
        "gateway": gateway,
        "white_label": True,
        "confirmations": 1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Проверяем, все ли ожидаемые ключи присутствуют в ответе
        if (
            data
            and isinstance(data.get("data"), dict)
            and isinstance(data["data"].get("invoice"), dict)
        ):
            invoice = data["data"]["invoice"]
            crypto_uri = invoice.get("crypto_uri")
            uniqid = invoice.get("uniqid")

            if crypto_uri and uniqid:
                try:
                    address, amount_param = crypto_uri.split("?")
                    # Вставляем пробел после двоеточия в адресе
                    if ":" in address:
                        protocol, addr = address.split(":", 1)
                        address = addr
                    amount = amount_param.split("=")[1]
                    return address, amount, uniqid, protocol, value
                except Exception as e:
                    logging.info(f"Error splitting crypto_uri: {crypto_uri}")
                    raise Exception(f"Error processing crypto_uri: {e}")
            else:
                logging.info(f"crypto_uri or uniqid is missing: {invoice}")
                raise Exception("Missing crypto_uri or uniqid in the response.")
        else:
            logging.info(f"Unexpected response structure: {data}")
            raise Exception("Unexpected data structure in response.")
    else:
        logging.info(
            f"Failed to create payment. Status Code: {response.status_code}, Response: {response.text}"
        )
        raise Exception(
            f"Failed to create payment. Status Code: {response.status_code}, Response: {response.text}"
        )
