from tgbot.mongo_db.db_api import subs


async def get_data_in_subs(filter_criteria):
    collection = subs
    cursor = collection.find(filter_criteria)
    data = await cursor.to_list(length=None)
    return data
