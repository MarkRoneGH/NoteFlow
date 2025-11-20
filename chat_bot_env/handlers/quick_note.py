from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from services.note_service import NoteService

router = Router()

@router.message(Command("quick"))
async def quick_note(message: Message):
    try:
        # Формат: /quick Заголовок | Описание | тег1, тег2
        parts = message.text.split('|')
        title = parts[0].replace('/quick', '').strip()
        
        if not title:
            await message.answer("❌ Укажите заголовок: /quick Заголовок | Описание | теги")
            return
        
        content = parts[1].strip() if len(parts) > 1 else None
        tags = [tag.strip() for tag in parts[2].split(',')] if len(parts) > 2 else []
        
        note = NoteService.create_note(
            user_id=message.from_user.id,
            title=title,
            content=content,
            tags=tags
        )
        
        if note:
            tags_text = f", теги: {', '.join(['#' + tag for tag in tags])}" if tags else ""
            await message.answer(f"✅ Быстрая заметка создана: {title}{tags_text}")
        else:
            await message.answer("❌ Ошибка при создании заметки")
            
    except Exception as e:
        await message.answer(
            "❌ Ошибка формата. Используйте:\n"
            "<code>/quick Заголовок | Описание | тег1, тег2</code>\n\n"
            "Пример:\n"
            "<code>/quick Покупки | Купить молоко и хлеб | продукты, магазин</code>"
        )