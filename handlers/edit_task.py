from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from states.task_states import TaskStates


def register_edit_task_handlers(dp: Dispatcher, db_pool):
    @dp.message(lambda m: m.text == "Редактировать задачу")
    async def edit_task_prompt(message: types.Message, state: FSMContext):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач для редактирования.")
                return
            task_list = "\n".join([f"{t['id']}: {t['title']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для редактирования:")
            await state.set_state(TaskStates.waiting_for_task_id_to_edit)

    @dp.message(TaskStates.waiting_for_task_id_to_edit)
    async def ask_new_title(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный ID задачи.")
            return

        await state.update_data(task_id=task_id)
        await message.answer("Введите новое название задачи:")
        await state.set_state(TaskStates.waiting_for_new_title)

    @dp.message(TaskStates.waiting_for_new_title)
    async def ask_new_description(message: types.Message, state: FSMContext):
        await state.update_data(new_title=message.text)
        await message.answer("Введите новое описание задачи:")
        await state.set_state(TaskStates.waiting_for_new_description)

    @dp.message(TaskStates.waiting_for_new_description)
    async def update_task(message: types.Message, state: FSMContext):
        data = await state.get_data()
        task_id = data["task_id"]
        new_title = data["new_title"]
        new_description = message.text

        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE tasks SET title=$1, description=$2 WHERE id=$3",
                new_title, new_description, task_id
            )
            if result.endswith("UPDATE 1"):
                await message.answer("Задача обновлена ✅")
            else:
                await message.answer("Ошибка при обновлении задачи ❌")
        await state.clear()
