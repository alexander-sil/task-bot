from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from states.task_states import TaskStates


def register_comment_task_handlers(dp: Dispatcher, db_pool):
    @dp.message(lambda m: m.text == "Комментировать задачу")
    async def comment_task_prompt(message: types.Message, state: FSMContext):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач для комментирования.")
                return
            task_list = "\n".join([f"{t['id']}: {t['title']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для комментария:")
            await state.set_state(TaskStates.waiting_for_task_id_to_comment)

    @dp.message(TaskStates.waiting_for_task_id_to_comment)
    async def get_comment(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный ID задачи.")
            return
        await state.update_data(task_id=task_id)
        await message.answer("Введите ваш комментарий:")
        await state.set_state(TaskStates.waiting_for_comment)

    @dp.message(TaskStates.waiting_for_comment)
    async def save_comment(message: types.Message, state: FSMContext):
        data = await state.get_data()
        task_id = data["task_id"]
        comment = message.text
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            await conn.execute(
                "INSERT INTO comments (task_id, user_id, content) VALUES ($1, $2, $3)",
                task_id, user_id, comment
            )
        await message.answer("Комментарий сохранён ✅")
        await state.clear()
