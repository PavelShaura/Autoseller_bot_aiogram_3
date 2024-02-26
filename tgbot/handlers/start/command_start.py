import logging
from typing import Union

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from pymongo.errors import DuplicateKeyError

from tgbot.mongo_db.db_api import users
from tgbot.phrasebook.lexicon_ru import LEXICON_RU
from tgbot.keyboards.reply import menu_keyboard

command_start_router = Router()


@command_start_router.callback_query(F.data == "to_menu")
@command_start_router.message(CommandStart(), flags={"throttling_key": "default"})
async def user_start(query: Union[Message, CallbackQuery]) -> None:
    """
    Handles the start command or callback query "to_menu".

    Args:
        query (Union[Message, CallbackQuery]): The incoming message or callback query.

    Returns:
        None
    """
    message: Message = query if isinstance(query, Message) else query.message
    await message.answer(text=LEXICON_RU["menu"], reply_markup=menu_keyboard)
    _id: int = message.from_user.id
    name: str = message.from_user.full_name
    username: str = message.from_user.username
    try:
        await users.insert_one(
            {
                "_id": message.from_user.id,
                "name": name,
                "username": username,
                "date": message.date,
            }
        )
        logging.info(f"{name} {username} came to see us!")
    except DuplicateKeyError:
        pass
