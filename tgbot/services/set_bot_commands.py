from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot) -> None:
    user_commands: list[BotCommand] = [
        BotCommand(command="start", description="Главное меню")
    ]
    await bot.set_my_commands(user_commands)
