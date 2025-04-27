from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, insert
from states.task_states import TaskStates
from models.models import User, Task, Comment

def register_comment_task_handlers(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Комментировать задачу")
    async def comment_task_prompt(message: types.Message, state: FSMContext):
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
                    await message.answer("У вас нет задач для комментирования.")
                    return

                task_list = "\n".join([f"{task.id}: {task.title}" for task in tasks])
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

        async with db_session() as session:
            async with session.begin():
                # Получаем user_id
                stmt_user = select(User.id).where(User.telegram_id == message.from_user.id)
                result_user = await session.execute(stmt_user)
                user_id = result_user.scalar_one_or_none()

                if not user_id:
                    await message.answer("Пользователь не найден.")
                    return

                # Вставляем новый комментарий
                stmt_insert = insert(Comment).values(task_id=task_id, user_id=user_id, content=comment)
                await session.execute(stmt_insert)

        await message.answer("Комментарий сохранён")
        await state.clear()
