from dataclasses import dataclass
from configparser import ConfigParser

@dataclass
class BotConfig:
    token: str

@dataclass
class DBConfig:
    user: str
    password: str
    host: str
    dbname: str

@dataclass
class Config:
    bot: BotConfig
    db: DBConfig

def load_config(path: str = "config.ini") -> Config:
    parser = ConfigParser()
    parser.read(path)
    return Config(
        bot=BotConfig(token=parser["bot"]["token"]),
        db=DBConfig(
            user=parser["database"]["user"],
            password=parser["database"]["password"],
            host=parser["database"]["host"],
            dbname=parser["database"]["dbname"]
        )
    )

