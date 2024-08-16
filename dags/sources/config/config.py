from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    chat_id: int


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str) -> Config:
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            chat_id=env('CHAT_ID')
        )
    )
