from aiogram import Dispatcher, types
from aiogram.filters import Command
from .common import main_kb

def register_start_handler(dp: Dispatcher, db_pool):
    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", message.from_user.id)
            if not user:
                await conn.execute("""
                    INSERT INTO users (telegram_id, first_name, last_name, username)
                    VALUES ($1, $2, $3, $4)
                """, message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                   message.from_user.username)
        await message.answer("Привет! Я бот для управления задачами.", reply_markup=main_kb)
