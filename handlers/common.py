from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать задачу")],
        [KeyboardButton(text="Удалить задачу")],
        [KeyboardButton(text="Редактировать задачу")],
        [KeyboardButton(text="Список задач")],
        [KeyboardButton(text="Комментировать задачу")]
    ],
    resize_keyboard=True
)
