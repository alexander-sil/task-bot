from asyncpg import create_pool as asyncpg_create_pool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import load_config  # Подключаем функцию load_config

# Загружаем конфигурацию
config = load_config("config.ini")  # Чтение конфигурации из config.ini

async def create_pool(config):
    return await asyncpg_create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.dbname,
        host=config.db.host
    )

# Формирование строки подключения для SQLAlchemy
DATABASE_URL = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.dbname}"

# Создание движка и сессии
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)