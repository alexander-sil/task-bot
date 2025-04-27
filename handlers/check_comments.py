from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from models.models import User, Task, Comment
from .states import TaskStates  # Добавляем TaskStates для разных состояний


def register_view_comments_handler(dp: Dispatcher, db_session):
    @dp.message(lambda m: m.text == "Посмотреть комментарии")
    async def view_comments_prompt(message: types.Message, state: FSMContext):
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
                await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи, чтобы увидеть комментарии:")

                # Устанавливаем новое состояние для ввода ID задачи
                await state.set_state(TaskStates.waiting_for_task_id_for_comments)

    @dp.message(TaskStates.waiting_for_task_id_for_comments)
    async def show_comments_for_task(message: types.Message, state: FSMContext):
        # Проверка, что сообщение действительно соответствует состоянию ожидания ID задачи
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный ID задачи.")
            return

        # Запрашиваем комментарии по ID задачи
        async with db_session() as session:
            async with session.begin():
                stmt_comments = select(Comment).where(Comment.task_id == task_id)
                result_comments = await session.execute(stmt_comments)
                comments = result_comments.scalars().all()

                if not comments:
                    await message.answer("Комментариев к этой задаче нет.")
                    return

                comments_text = "\n\n".join([f"{comment.content} (от {comment.user_id})" for comment in comments])
                await message.answer(f"Комментарии:\n{comments_text}")

        await state.clear()  # Очистка состояния после выполнения действия

