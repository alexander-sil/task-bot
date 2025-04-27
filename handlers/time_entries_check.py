from aiogram import Dispatcher, types
from sqlalchemy import select
from models.models import User, Task, TimeEntry

def register_view_time_entries_handler(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Посмотреть учет времени")
    async def view_time_entries_prompt(message: types.Message):
        async with db_session() as session:
            async with session.begin():
                # Проверяем наличие пользователя в базе
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
                    await message.answer("У вас нет задач.")
                    return

                # Выводим задачи
                task_list = "\n".join([f"{task.id}: {task.title}" for task in tasks])
                await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи, чтобы увидеть учет времени:")

        @dp.message(lambda m: m.text.isdigit())  # Обрабатываем только числовые ID задач
        async def show_time_entries_for_task(message: types.Message):
            task_id = int(message.text)

            async with db_session() as session:
                async with session.begin():
                    # Получаем записи учета времени для выбранной задачи
                    stmt_time_entries = select(TimeEntry).where(TimeEntry.task_id == task_id)
                    result_time_entries = await session.execute(stmt_time_entries)
                    time_entries = result_time_entries.scalars().all()

                    if not time_entries:
                        await message.answer("Нет записей учета времени по этой задаче.")
                        return

                    # Формируем и выводим информацию по времени
                    entries_text = "\n\n".join([
                        f"Начало: {entry.start_time}\nКонец: {entry.end_time}\nДлительность: {entry.duration}"
                        for entry in time_entries
                    ])
                    await message.answer(f"Учет времени:\n{entries_text}")
