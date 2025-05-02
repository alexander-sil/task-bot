from aiogram import Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import text, select
from models.models import User  # Убедись, что модель User импортирована
import pandas as pd
import io
from datetime import timedelta

def register_info_handler(dp: Dispatcher, db_session):
    @dp.message(Command("info"))
    async def info_handler(message: types.Message):
        async with db_session() as session:
            async with session.begin():
                # Получаем пользователя по telegram_id
                result = await session.execute(
                    select(User).where(User.telegram_id == message.from_user.id)
                )
                user = result.scalar_one_or_none()

                if not user or not user.is_admin:
                    await message.answer("У вас нет прав для использования этой команды.")
                    return

                # Выполняем запрос к представлению task_details
                query = text("SELECT * FROM task_details")
                result = await session.execute(query)
                rows = result.fetchall()

                if not rows:
                    await message.answer("Нет данных для отображения.")
                    return

                # Преобразуем в DataFrame
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)

                # Форматируем поле total_time_spent
                def format_interval(val):
                    if isinstance(val, timedelta):
                        total_seconds = int(val.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    return "00:00:00"

                if 'total_time_spent' in df.columns:
                    df['total_time_spent'] = df['total_time_spent'].apply(format_interval)

                # Генерируем Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name="Task Details")
                output.seek(0)

        await message.answer_document(
            types.BufferedInputFile(output.read(), filename="task_details.xlsx"),
            caption="Вот ваш отчет по задачам."
        )
