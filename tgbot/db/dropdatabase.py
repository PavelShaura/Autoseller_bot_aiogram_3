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

    await users.delete_many({})
    await payments.delete_many({})
    await subs.delete_many({})
    await files.delete_many({})
    await trial.delete_many({})


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drop_collection_data())
