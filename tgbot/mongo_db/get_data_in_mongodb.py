from tgbot.mongo_db.db_api import subs
from typing import Any, Dict, List


async def get_data_in_subs(filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieve data from the 'subs' collection based on the provided filter criteria.

    Args:
        filter_criteria (Dict[str, Any]): The filter criteria to be applied to the database query.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the retrieved data.

    This function retrieves data from the 'subs' collection in the MongoDB database based on the provided
    filter criteria. It returns a list of dictionaries, with each dictionary representing a document
    retrieved from the collection.
    """
    collection = subs
    cursor = collection.find(filter_criteria)
    data = await cursor.to_list(length=None)
    return data
