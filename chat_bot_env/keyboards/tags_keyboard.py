from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Tag
from typing import List

def get_tags_keyboard(tags: List[Tag], note_id: int = None):
    keyboard = []
    
    # Показываем по 2 тега в строке для лучшего отображения
    for i in range(0, len(tags), 2):
        row = []
        for tag in tags[i:i+2]:
            if note_id:
                # Для добавления существующего тега к заметке
                callback_data = f"add_tag_{tag.id}_{note_id}"
            else:
                # Для фильтрации по тегу
                callback_data = f"filter_tag_{tag.name}"
            row.append(InlineKeyboardButton(text=f"#{tag.name}", callback_data=callback_data))
        keyboard.append(row)
    
    # Добавляем кнопку создания нового тега если есть note_id
    if note_id:
        keyboard.append([
            InlineKeyboardButton(text="➕ Создать новый тег", callback_data=f"new_tag_{note_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к заметкам", callback_data="back_to_notes")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_tags_choice_keyboard(note_id: int):
    """Клавиатура выбора действия с тегами для новой заметки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎯 Создать новый тег", callback_data=f"new_tag_{note_id}"),
            ],
            [
                InlineKeyboardButton(text="📋 Выбрать из моих тегов", callback_data=f"show_my_tags_{note_id}"),
            ],
            [
                InlineKeyboardButton(text="⏩ Пропустить", callback_data=f"skip_tags_{note_id}"),
            ]
        ]
    )