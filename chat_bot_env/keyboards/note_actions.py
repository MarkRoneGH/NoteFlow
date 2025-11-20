from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.repository import NoteRepository

def get_note_actions(note_id: int, note_status: str = "active", is_pinned: bool = False):
    """Создает клавиатуру действий для заметки с учетом текущего состояния"""
    
    # Тексты кнопок в зависимости от состояния
    complete_text = "✅ Выполнено" if note_status == "active" else "↩️ Вернуть в работу"
    pin_text = "📌 Открепить" if is_pinned else "📌 Закрепить"
    
    keyboard = [
        [
            InlineKeyboardButton(text=complete_text, callback_data=f"complete_{note_id}"),
            InlineKeyboardButton(text=pin_text, callback_data=f"pin_{note_id}")
        ],
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{note_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{note_id}")
        ],
        [
            InlineKeyboardButton(text="⏰ Напомнить", callback_data=f"remind_{note_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_edit_actions(note_id: int):
    """Клавиатура для редактирования заметки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Заголовок", callback_data=f"edit_title_{note_id}"),
                InlineKeyboardButton(text="📄 Содержание", callback_data=f"edit_content_{note_id}")
            ],
            [
                InlineKeyboardButton(text="🏷 Теги", callback_data=f"edit_tags_{note_id}"),
                InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_note_{note_id}")
            ]
        ]
    )