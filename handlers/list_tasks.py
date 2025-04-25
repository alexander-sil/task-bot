from aiogram import Dispatcher, types


def register_list_task_handler(dp: Dispatcher, db_pool):
    @dp.message(lambda m: m.text == "Список задач")
    async def list_tasks(message: types.Message):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title, description FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач.")
                return
            task_list = "\n\n".join(
                [f"ID: {t['id']}\nНазвание: {t['title']}\nОписание: {t['description']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n\n{task_list}")
