import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler
import betterlogging as bl

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from tgbot import apscheduler
from tgbot import middlewares
from tgbot import services
from tgbot.handlers import routers

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await services.broadcaster.broadcast(
        bot, admin_ids, "Бот запущен! Вы администратор!"
    )


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(middlewares.ConfigMiddleware(config))
    dp.callback_query.outer_middleware(middlewares.ConfigMiddleware(config))
    dp.message.middleware(middlewares.ThrottlingMiddleware())
    dp.callback_query.middleware(middlewares.ThrottlingMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())


def register_logger():
    log_format = (
        "%(filename)s [LINE:%(lineno)d] #%(levelname)-6s [%(asctime)s]  %(message)s"
    )
    date_format = "%d.%m.%Y %H:%M:%S"

    logging.basicConfig(
        format=log_format,
        datefmt=date_format,
        level=log_level,
    )
    logger = logging.getLogger()

    logger.setLevel(log_level)

    log_file_path = os.path.join("logs", "bot.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
    )  # Maximum file size 10 MB, 5 files stored
    file_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    logger.addHandler(file_handler)

    logger.info("Starting bot")


async def main():
    from tgbot.config import config

    register_logger()

    storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    apscheduler.scheduler.add_job(
        apscheduler.notification_to_user,
        trigger="interval",
        days=1,
        kwargs={"bot": bot},
    )
    apscheduler.scheduler.add_job(
        apscheduler.notification_to_admin_group,
        trigger="interval",
        days=1,
        kwargs={"bot": bot},
    )

    apscheduler.scheduler.start()

    dp.update.middleware.register(
        middlewares.SchedulerMiddleware(apscheduler.scheduler)
    )

    for router in routers:
        dp.include_router(router)

    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")

    register_global_middlewares(dp, config)

    await services.set_main_menu(bot)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Stopping bot")
