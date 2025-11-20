from typing import List
from database.models import Note

def format_note(note: Note, tags: List[str] = None) -> str:
    """
    Форматирует заметку для отображения
    
    Args:
        note: Объект заметки
        tags: Список названий тегов (опционально)
    """
    status_icon = "✅" if note.status == 'completed' else "📝"
    pinned_icon = "📌 " if note.is_pinned else ""
    
    # Добавляем теги если они переданы
    tags_text = ""
    if tags:
        tags_text = f"\n🏷 Теги: {', '.join(['#' + tag for tag in tags])}"
    
    return (f"{pinned_icon}{status_icon} <b>{note.title}</b>\n"
            f"{note.content or 'Без описания'}{tags_text}\n"
            f"<i>Создано: {note.created_at.strftime('%d.%m.%Y %H:%M')}</i>")

def format_notes_list(notes: List[Note]) -> str:
    """Форматирует список заметок для отображения"""
    if not notes:
        return "Заметок не найдено"
    
    result = "📋 Ваши заметки:\n\n"
    for note in notes:
        status_icon = "✅" if note.status == 'completed' else "📝"
        pinned_icon = "📌 " if note.is_pinned else ""
        
        # Получаем теги для заметки (нужно будет передавать их отдельно)
        # Пока оставим без тегов в общем списке, они будут в детальном просмотре
        result += f"{pinned_icon}{status_icon} {note.title}\n"
    
    return result