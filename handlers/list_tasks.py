# handlers/list_tasks.py
from aiogram import Dispatcher, types
from sqlalchemy import select
from models.models import Task, User

def register_list_task_handler(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Список задач")
    async def list_tasks(message: types.Message):
        async with db_session() as session:
            async with session.begin():  # открываем транзакцию
                # Получаем пользователя по telegram_id
                stmt_user = select(User.id).where(User.telegram_id == message.from_user.id)
                result_user = await session.execute(stmt_user)
                user_id = result_user.scalar_one_or_none()

                if not user_id:
                    await message.answer("Пользователь не найден.")
                    return

                # Получаем список задач пользователя
                stmt_tasks = select(Task).where(Task.user_id == user_id)
                result_tasks = await session.execute(stmt_tasks)
                tasks = result_tasks.scalars().all()

                if not tasks:
                    await message.answer("У вас нет задач.")
                    return

                # Формируем строку с задачами для ответа
                task_list = "\n\n".join(
                    [f"ID: {task.id}\nНазвание: {task.title}\nОписание: {task.description}" for task in tasks]
                )
                await message.answer(f"Ваши задачи:\n\n{task_list}")
