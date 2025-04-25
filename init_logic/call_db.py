import logging
import asyncpg
from config import load_config
from pathlib import Path

logging.basicConfig(level=logging.INFO)

config = load_config()

# Путь к папке sql
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"

def read_sql_file(filename: str) -> str:
    with open(SQL_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

async def init_db():
    db_conf = config.db
    conn = await asyncpg.connect(
        user=db_conf.user,
        password=db_conf.password,
        database=db_conf.dbname,
        host=db_conf.host,
    )
    print("Подключение к БД успешно")

    # Проверка наличия таблиц
    table_check_sql = read_sql_file("table_check.sql")
    result = await conn.fetch(table_check_sql)
    existing_tables = {row["table_name"] for row in result}

    expected_tables = {'users', 'tasks', 'time_entries', 'comments'}
    if expected_tables.issubset(existing_tables):
        print("Все таблицы уже существуют")
    else:
        print("Создание недостающих таблиц")
        create_sql = read_sql_file("create_tables.sql")
        await conn.execute(create_sql)
        print("Таблицы успешно созданы")

    # Применение вспомогательных объектов (триггеры, представление, индексы)
    print("Применение вспомогательных объектов")

    helpers_sql = read_sql_file("create_helpers.sql")

    for statement in helpers_sql.split(";"):
        stmt = statement.strip()
        if stmt:
            try:
                await conn.execute(stmt + ";")
            except asyncpg.DuplicateObjectError as e:
                print(f"Объект уже существует, пропускаем:\n{e}")
            except Exception as e:
                print(f"Ошибка при выполнении SQL:\n{stmt}\n{e}")


    await conn.close()
