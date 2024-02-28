from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    name: str
    port: int = 27017


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    channel_id: int
    selix_api_key: str
    sub_image_folder: str
    trial_image_folder: str

@dataclass
class Miscellaneous:
    yoomoney_token: str
    yoomoney_wallet: str
    client_id: str
    redirect_url: str


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous = None
    db: DbConfig = None


def load_config(path: str = ".env") -> Config:
    """
    Loads the configuration from the environment variables.

    Args:
        path (str): The path to the environment file. Default is ".env".

    Returns:
        Config: The loaded configuration.
    """
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=env.list("ADMINS", subcast=int),
            channel_id=env.int("CHANNEL_INFO_ID"),
            selix_api_key=env.str("SELLIX_API_KEY"),
            sub_image_folder=env.str("SUB_IMAGE_FOLDER"),
            trial_image_folder=env.str("TRIAL_IMAGE_FOLDER")
        ),
        db=DbConfig(
            host=env.str("DB_HOST"), port=env.int("DB_PORT"), name=env.str("DB_NAME")
        ),
        misc=Miscellaneous(
            yoomoney_token=env.str("YOOMONEY_TOKEN"),
            yoomoney_wallet=env.str("YOOMONEY_WALLET"),
            client_id=env.str("YOOMONEY_CLIENT_ID"),
            redirect_url=env.str("YOOMONEY_REDIRECT_URL"),
        ),
    )


config = load_config(".env")
