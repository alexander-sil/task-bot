from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from states.task_states import TaskStates
from models.models import User, Task
from sqlalchemy.ext.asyncio import async_sessionmaker

def register_create_task_handlers(dp: Dispatcher, db_session: async_sessionmaker):
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

        async with db_session() as session:  # Используем async_session
            stmt_select = select(User.id).where(User.telegram_id == message.from_user.id)
            result = await session.execute(stmt_select)
            user_id = result.scalar_one_or_none()

            if user_id is None:
                await message.answer("Ошибка: пользователь не найден в базе данных.")
                return

            new_task = Task(user_id=user_id, title=title, description=description)
            session.add(new_task)
            await session.commit()

        await message.answer("Задача создана")
