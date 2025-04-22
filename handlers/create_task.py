from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from states.task_states import TaskStates


def register_create_task_handlers(dp: Dispatcher, db_pool):
    @dp.message(lambda m: m.text == "Создать задачу")
    async def create_task_prompt(message: types.Message, state: FSMContext):
        await message.answer("Введите название задачи:")
        await state.set_state(TaskStates.waiting_for_title)

    @dp.message(TaskStates.waiting_for_title)
    async def get_title(message: types.Message, state: FSMContext):
        await state.update_data(title=message.text)
        await state.set_state(TaskStates.waiting_for_description)
        await message.answer("Введите описание задачи:")

    @dp.message(TaskStates.waiting_for_description)
    async def get_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        title = data["title"]
        description = message.text
        await state.clear()

        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            await conn.execute("""
                INSERT INTO tasks (user_id, title, description)
                VALUES ($1, $2, $3)
            """, user_id, title, description)
        await message.answer("Задача создана ✅")
