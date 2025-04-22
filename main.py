import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher
from config import load_config
from db import create_pool
from handlers import register_handlers
from pathlib import Path

# Настройка логгирования и конфигурации
logging.basicConfig(level=logging.INFO)
config = load_config()

bot = Bot(token=config.bot.token)
dp = Dispatcher()

# Директория SQL-файлов
SQL_DIR = Path(__file__).parent / "sql"

def read_sql_file(filename: str) -> str:
    with open(SQL_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

async def main():
    db_pool = await create_pool(config)
    register_handlers(dp, db_pool)
    await dp.start_polling(bot)

async def init_db():
    db_conf = config.db
    conn = await asyncpg.connect(
        user=db_conf.user,
        password=db_conf.password,
        database=config.db.dbname,
        host=db_conf.host,
    )
    print("✅ Подключение к БД успешно.")

    table_check_sql = read_sql_file("table_check.sql")
    result = await conn.fetch(table_check_sql)
    existing_tables = {row["table_name"] for row in result}

    expected_tables = {'users', 'tasks', 'time_entries', 'comments'}
    if expected_tables.issubset(existing_tables):
        print("✅ Все таблицы уже существуют.")
    else:
        print("📦 Создание недостающих таблиц...")
        create_sql = read_sql_file("create_tables.sql")
        await conn.execute(create_sql)
        print("✅ Таблицы успешно созданы.")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(main())
