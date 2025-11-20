from database.repository import NoteRepository, TagRepository
from database.models import Note
from database.connection import get_connection 
from typing import List

class NoteService:
    @staticmethod
    def create_note(user_id: int, title: str, content: str = None, tags: List[str] = None) -> Note:
        note = NoteRepository.create(user_id, title, content)
        
        if tags and note:
            for tag_name in tags:
                tag = TagRepository.get_or_create(user_id, tag_name.strip())
                if tag:
                    TagRepository.add_to_note(note.id, tag.id)
        
        return note

    @staticmethod
    def get_user_notes(user_id: int, status: str = None, tag: str = None) -> List[Note]:
        return NoteRepository.get_user_notes(user_id, status, tag)

    @staticmethod
    def complete_note(note_id: int):
        NoteRepository.update_status(note_id, "completed")

    @staticmethod
    def toggle_pin(note_id: int) -> bool:
        return NoteRepository.toggle_pin(note_id)

    @staticmethod
    def delete_note(note_id: int):
        NoteRepository.delete(note_id)

    @staticmethod
    def search_notes(user_id: int, query: str) -> List[Note]:
        return NoteRepository.search(user_id, query)

    @staticmethod
    def update_note_status(note_id: int, status: str):
        """Обновляет статус заметки (для возврата в работу)"""
        NoteRepository.update_status(note_id, status)

    @staticmethod
    def get_note_by_id(note_id: int) -> Note:
        """Получает заметку по ID"""
        return NoteRepository.get_by_id(note_id)

    # ДОБАВЛЯЕМ НОВЫЕ МЕТОДЫ ДЛЯ РЕДАКТИРОВАНИЯ
    @staticmethod
    def update_note_title(note_id: int, new_title: str):
        """Обновляет заголовок заметки"""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE notes SET title = %s, updated_at = NOW() WHERE id = %s",
            (new_title, note_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def update_note_content(note_id: int, new_content: str):
        """Обновляет содержание заметки"""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE notes SET content = %s, updated_at = NOW() WHERE id = %s",
            (new_content, note_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()