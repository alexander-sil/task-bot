from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать задачу"),
            KeyboardButton(text="Удалить задачу")
        ],
        [
            KeyboardButton(text="Редактировать задачу"),
            KeyboardButton(text="Список задач")
        ],
        [
            KeyboardButton(text="Комментировать задачу"),
            KeyboardButton(text="Посмотреть комментарии")
        ],
        [
            KeyboardButton(text="Посмотреть учет времени"),
            KeyboardButton(text="Добавить учет времени")
        ]
    ],
    resize_keyboard=True
)

