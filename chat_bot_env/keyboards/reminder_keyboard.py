from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_reminder_keyboard(note_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="10 мин", callback_data=f"reminder_10_{note_id}"),
                InlineKeyboardButton(text="1 час", callback_data=f"reminder_60_{note_id}"),
                InlineKeyboardButton(text="3 часа", callback_data=f"reminder_180_{note_id}")
            ],
            [
                InlineKeyboardButton(text="1 день", callback_data=f"reminder_1440_{note_id}"),
                InlineKeyboardButton(text="Ежедневно", callback_data=f"repeat_daily_{note_id}"),
                InlineKeyboardButton(text="Еженедельно", callback_data=f"repeat_weekly_{note_id}")
            ]
        ]
    )