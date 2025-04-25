import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher
from config import load_config
from db import create_pool
from handlers import register_handlers
from pathlib import Path
from init_logic import call_db

# Настройка логгирования и конфигурации
logging.basicConfig(level=logging.INFO)
config = load_config()

bot = Bot(token=config.bot.token)
dp = Dispatcher()


async def main():
    db_pool = await create_pool(config)
    register_handlers(dp, db_pool)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(call_db.init_db())
    asyncio.run(main())
