from aiogram import Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import select
from models.models import User
from keyboards.main import main_kb

def register_start_handler(dp: Dispatcher, db_session):
    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        async with db_session() as session:
            async with session.begin():  # открываем транзакцию
                stmt = select(User).where(User.telegram_id == message.from_user.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    new_user = User(
                        telegram_id=message.from_user.id,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name,
                        username=message.from_user.username,
                    )
                    session.add(new_user)
                    # session.begin() автоматически закоммитит изменения

        await message.answer("Привет! Я бот для управления задачами.", reply_markup=main_kb)

