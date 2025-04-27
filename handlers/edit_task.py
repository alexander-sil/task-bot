# handlers/edit_task.py
from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from states.task_states import TaskStates
from models.models import User, Task

def register_edit_task_handlers(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Редактировать задачу")
    async def edit_task_prompt(message: types.Message, state: FSMContext):
        async with db_session() as session:
            async with session.begin():
                # Получаем user_id по telegram_id
                stmt_user = select(User.id).where(User.telegram_id == message.from_user.id)
                result_user = await session.execute(stmt_user)
                user_id = result_user.scalar_one_or_none()

                if not user_id:
                    await message.answer("Пользователь не найден.")
                    return

                # Получаем задачи пользователя
                stmt_tasks = select(Task).where(Task.user_id == user_id)
                result_tasks = await session.execute(stmt_tasks)
                tasks = result_tasks.scalars().all()

                if not tasks:
                    await message.answer("У вас нет задач для редактирования.")
                    return

                task_list = "\n".join([f"{task.id}: {task.title}" for task in tasks])
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

        async with db_session() as session:
            async with session.begin():
                # Получаем задачу для обновления
                stmt_task = select(Task).where(Task.id == task_id)
                result_task = await session.execute(stmt_task)
                task = result_task.scalar_one_or_none()

                if not task:
                    await message.answer("Задача не найдена ❌")
                    return

                # Обновляем задачу
                stmt_update = update(Task).where(Task.id == task_id).values(title=new_title, description=new_description)
                await session.execute(stmt_update)

        await message.answer("Задача обновлена ✅")
        await state.clear()
