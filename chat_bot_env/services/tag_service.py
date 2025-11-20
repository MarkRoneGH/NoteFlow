from database.repository import TagRepository
from database.models import Tag
from typing import List, Optional

class TagService:
    @staticmethod
    def get_user_tags(user_id: int) -> List[Tag]:
        return TagRepository.get_user_tags(user_id)

    @staticmethod
    def create_tag(user_id: int, name: str) -> Optional[Tag]:
        """Создает новый тег"""
        return TagRepository.get_or_create(user_id, name)

    @staticmethod
    def add_tag_to_note(user_id: int, note_id: int, tag_name: str) -> Optional[Tag]:
        """Добавляет тег к заметке"""
        tag = TagRepository.get_or_create(user_id, tag_name)
        if tag:
            TagRepository.add_to_note(note_id, tag.id)
        return tag

    @staticmethod
    def get_by_id(tag_id: int) -> Optional[Tag]:
        """Получает тег по ID"""
        from database.repository import TagRepository
        return TagRepository.get_by_id(tag_id)

    # ДОБАВЛЯЕМ НОВЫЙ МЕТОД ДЛЯ ПРОВЕРКИ ПРИВЯЗКИ
    @staticmethod
    def get_note_tags(note_id: int) -> List[Tag]:
        """Получает все теги привязанные к заметке"""
        from database.repository import TagRepository
        return TagRepository.get_note_tags(note_id)