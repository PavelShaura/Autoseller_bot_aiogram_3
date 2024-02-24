import asyncio

from tgbot.mongo_db.db_api import users, payments, subs, files, trial


async def drop_collection_data():
    await users.delete_many({})
    await payments.delete_many({})
    await subs.delete_many({})
    await files.delete_many({})
    await trial.delete_many({})


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drop_collection_data())
    loop.close()
