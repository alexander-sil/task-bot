from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from models.models import User, Task, TimeEntry
from datetime import datetime
from .states import TaskStates


def register_time_entry_handlers(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Добавить учет времени")
    async def add_time_entry_prompt(message: types.Message, state: FSMContext):
        async with db_session() as session:
            async with session.begin():
                stmt_user = select(User.id).where(User.telegram_id == message.from_user.id)
                result_user = await session.execute(stmt_user)
                user_id = result_user.scalar_one_or_none()

                if not user_id:
                    await message.answer("Пользователь не найден.")
                    return

                stmt_tasks = select(Task).where(Task.user_id == user_id)
                result_tasks = await session.execute(stmt_tasks)
                tasks = result_tasks.scalars().all()

                if not tasks:
                    await message.answer("У вас нет задач.")
                    return

                task_list = "\n".join([f"{task.id}: {task.title}" for task in tasks])
                await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи, для которой хотите добавить учет времени:")
                await state.set_state(TaskStates.waiting_for_task_id)

    @dp.message(TaskStates.waiting_for_task_id)
    async def ask_start_time(message: types.Message, state: FSMContext):
        # Проверка, что сообщение действительно соответствует состоянию ожидания ID задачи
        if not message.text.isdigit():
            return  # Если не цифра, игнорируем сообщение

        task_id = int(message.text)
        await state.update_data(task_id=task_id)
        await message.answer("Введите дату и время начала в формате ГГГГ-ММ-ДД ЧЧ:ММ (например, 2025-04-27 15:00):")
        await state.set_state(TaskStates.waiting_for_start_time)

    @dp.message(TaskStates.waiting_for_start_time)
    async def ask_end_time(message: types.Message, state: FSMContext):
        try:
            start_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты и времени. Попробуйте снова.")
            return

        await state.update_data(start_time=start_time)
        await message.answer("Введите дату и время окончания в формате ГГГГ-ММ-ДД ЧЧ:ММ:")
        await state.set_state(TaskStates.waiting_for_end_time)

    @dp.message(TaskStates.waiting_for_end_time)
    async def save_time_entry(message: types.Message, state: FSMContext):
        try:
            end_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты и времени. Попробуйте снова.")
            return

        data = await state.get_data()
        start_time = data["start_time"]
        task_id = data["task_id"]

        if end_time <= start_time:
            await message.answer("Время окончания должно быть позже времени начала.")
            return

        duration = end_time - start_time

        async with db_session() as session:
            async with session.begin():
                new_entry = TimeEntry(
                    task_id=task_id,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration
                )
                session.add(new_entry)

        await message.answer("Учет времени добавлен ✅")
        await state.clear()
