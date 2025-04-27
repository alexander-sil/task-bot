from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete
from states.task_states import TaskStates
from models.models import User, Task

def register_delete_task_handlers(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Удалить задачу")
    async def delete_task_prompt(message: types.Message, state: FSMContext):
        async with db_session() as session:
            async with session.begin():  # открываем транзакцию
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
                    await message.answer("У вас нет задач для удаления.")
                    return

                task_list = "\n".join([f"{task.id}: {task.title}" for task in tasks])
                await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для удаления:")
                await state.set_state(TaskStates.waiting_for_task_id_to_delete)

    @dp.message(TaskStates.waiting_for_task_id_to_delete)
    async def delete_task(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный числовой ID задачи.")
            return

        async with db_session() as session:
            async with session.begin():
                # Получаем user_id по telegram_id
                stmt_user = select(User.id).where(User.telegram_id == message.from_user.id)
                result_user = await session.execute(stmt_user)
                user_id = result_user.scalar_one_or_none()

                if not user_id:
                    await message.answer("Пользователь не найден.")
                    return

                # Проверяем, существует ли задача
                stmt_task = select(Task).where(Task.id == task_id, Task.user_id == user_id)
                result_task = await session.execute(stmt_task)
                task = result_task.scalar_one_or_none()

                if not task:
                    await message.answer("Задача с таким ID не найдена ❌")
                    return

                # Удаляем задачу
                stmt_delete = delete(Task).where(Task.id == task_id)
                await session.execute(stmt_delete)

        await message.answer("Задача удалена ✅")
        await state.clear()
