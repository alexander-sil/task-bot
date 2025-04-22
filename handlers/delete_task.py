from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from states.task_states import TaskStates


def register_delete_task_handlers(dp: Dispatcher, db_pool):
    @dp.message(lambda m: m.text == "Удалить задачу")
    async def delete_task_prompt(message: types.Message, state: FSMContext):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач для удаления.")
                return
            task_list = "\n".join([f"{t['id']}: {t['title']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для удаления:")
            await state.set_state(TaskStates.waiting_for_task_id_to_delete)

    @dp.message(TaskStates.waiting_for_task_id_to_delete)
    async def delete_task(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный числовой ID задачи.")
            return

        async with db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM tasks WHERE id=$1", task_id)
            if result.endswith("DELETE 1"):
                await message.answer("Задача удалена ✅")
            else:
                await message.answer("Задача с таким ID не найдена ❌")
        await state.clear()
