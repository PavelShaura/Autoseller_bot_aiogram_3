from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from tgbot.config import config


async def drop_collection_data():
    client = AsyncIOMotorClient(host=config.db.host, port=config.db.port)
    db = client[config.db.name]
    users = db["users"]
    payments = db["payments"]
    subs = db["subs"]
    files = db["files"]
    trial = db["trial"]

    # Удалить все данные из коллекции "users"
    await users.delete_many({})

    # Удалить все данные из коллекции "payments"
    await payments.delete_many({})

    # Удалить все данные из коллекции "subs"
    await subs.delete_many({})

    # Удалить все данные из коллекции "files"
    await files.delete_many({})

    # Удалить все данные из коллекции "trial"
    await trial.delete_many({})  # Пустой фильтр {}

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drop_collection_data())
