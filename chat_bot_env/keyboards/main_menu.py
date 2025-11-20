from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Создать заметку"), KeyboardButton(text="📋 Мои заметки")],
            [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="🏷 Мои теги")],
            [KeyboardButton(text="✅ Выполненные"), KeyboardButton(text="📌 Закрепленные")]
        ],
        resize_keyboard=True
    )