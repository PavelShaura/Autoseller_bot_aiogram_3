from motor.motor_asyncio import AsyncIOMotorClient

from tgbot.config import config

client = AsyncIOMotorClient(host=config.db.host, port=config.db.port)

db = client[config.db.name]

users = db["users"]
payments = db["payments"]
subs = db["subs"]
files = db["files"]
trial = db["trial"]
