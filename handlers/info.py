from aiogram import Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import text
import pandas as pd
import io
from datetime import timedelta

def register_info_handler(dp: Dispatcher, db_session):
    @dp.message(Command("info"))
    async def info_handler(message: types.Message):
        async with db_session() as session:
            async with session.begin():
                # Выполняем текстовый SQL-запрос к представлению
                # TODO Придумать как запихнуть это в модель данных БД
                query = text("SELECT * FROM task_details")
                result = await session.execute(query)
                rows = result.fetchall()

                if not rows:
                    await message.answer("Нет данных для отображения.")
                    return

                # Получаем имена столбцов
                columns = result.keys()

                # Преобразуем данные в DataFrame
                df = pd.DataFrame(rows, columns=columns)

                # Преобразуем поле total_time_spent в формат "HH:MM:SS"
                def format_interval(val):
                    if isinstance(val, timedelta):
                        total_seconds = int(val.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    return "00:00:00"

                if 'total_time_spent' in df.columns:
                    df['total_time_spent'] = df['total_time_spent'].apply(format_interval)

                # Сохраняем в Excel-файл в памяти
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name="Task Details")

                output.seek(0)  # Перемещаемся в начало файла

        # Отправляем файл пользователю
        await message.answer_document(
            types.BufferedInputFile(output.read(), filename="task_details.xlsx"),
            caption="Вот ваш отчет по задачам."
        )
