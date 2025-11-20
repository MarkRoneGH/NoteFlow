from database.connection import get_connection
from database.models import User, Note, Tag, Reminder
from typing import List, Optional


class UserRepository:
    @staticmethod
    def get_or_create(user_id: int, username: str = None, first_name: str = None) -> User:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (id, username, first_name) VALUES (%s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username, first_name = EXCLUDED.first_name "
            "RETURNING id, username, first_name, created_at",
            (user_id, username, first_name)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return User(*result) if result else None


class NoteRepository:
    @staticmethod
    def create(user_id: int, title: str, content: str = None) -> Note:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s) "
            "RETURNING id, user_id, title, content, status, is_pinned, created_at, updated_at",
            (user_id, title, content)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return Note(*result) if result else None

    @staticmethod
    def get_by_id(note_id: int) -> Optional[Note]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, user_id, title, content, status, is_pinned, created_at, updated_at "
            "FROM notes WHERE id = %s",
            (note_id,)
        )
        result = cur.fetchone()

        cur.close()
        conn.close()

        return Note(*result) if result else None

    @staticmethod
    def get_user_notes(user_id: int, status: str = None, tag: str = None) -> List[Note]:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT DISTINCT n.id, n.user_id, n.title, n.content, n.status, n.is_pinned, n.created_at, n.updated_at
            FROM notes n
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags t ON nt.tag_id = t.id
            WHERE n.user_id = %s
        """
        params = [user_id]

        if status:
            query += " AND n.status = %s"
            params.append(status)

        if tag:
            query += " AND t.name = %s"
            params.append(tag)

        query += " ORDER BY n.is_pinned DESC, n.created_at DESC"

        cur.execute(query, params)
        results = cur.fetchall()

        cur.close()
        conn.close()

        return [Note(*row) for row in results]

    @staticmethod
    def update_status(note_id: int, status: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE notes SET status = %s, updated_at = NOW() WHERE id = %s",
            (status, note_id)
        )

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def toggle_pin(note_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE notes SET is_pinned = NOT is_pinned, updated_at = NOW() "
            "WHERE id = %s RETURNING is_pinned",
            (note_id,)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return result[0] if result else False

    @staticmethod
    def delete(note_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def search(user_id: int, query: str) -> List[Note]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, user_id, title, content, status, is_pinned, created_at, updated_at "
            "FROM notes WHERE user_id = %s AND (title ILIKE %s OR content ILIKE %s) "
            "ORDER BY created_at DESC",
            (user_id, f"%{query}%", f"%{query}%")
        )
        results = cur.fetchall()

        cur.close()
        conn.close()

        return [Note(*row) for row in results]


class TagRepository:
    @staticmethod
    def get_or_create(user_id: int, name: str) -> Tag:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO tags (user_id, name) VALUES (%s, %s) "
            "ON CONFLICT (user_id, name) DO UPDATE SET name = EXCLUDED.name "
            "RETURNING id, user_id, name",
            (user_id, name)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return Tag(*result) if result else None

    @staticmethod
    def add_to_note(note_id: int, tag_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO note_tags (note_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (note_id, tag_id)
        )

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_user_tags(user_id: int) -> List[Tag]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, user_id, name FROM tags WHERE user_id = %s ORDER BY name",
            (user_id,)
        )
        results = cur.fetchall()

        cur.close()
        conn.close()

        return [Tag(*row) for row in results]


class ReminderRepository:
    @staticmethod
    def create(note_id: int, reminder_time: str, reminder_type: str = 'once') -> Reminder:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO reminders (note_id, reminder_time, reminder_type) "
            "VALUES (%s, %s, %s) RETURNING id, note_id, reminder_time, reminder_type, is_active, created_at",
            (note_id, reminder_time, reminder_type)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return Reminder(*result) if result else None

    @staticmethod
    def get_pending_reminders():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT r.id, r.note_id, r.reminder_time, r.reminder_type, r.is_active, r.created_at, "
            "n.title, n.content, u.id as user_id "
            "FROM reminders r "
            "JOIN notes n ON r.note_id = n.id "
            "JOIN users u ON n.user_id = u.id "
            "WHERE r.reminder_time <= NOW() AND r.is_active = TRUE"
        )
        results = cur.fetchall()

        cur.close()
        conn.close()

        return results

    @staticmethod
    def get_by_id(tag_id: int) -> Optional[Tag]:
        """Получает тег по ID"""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, user_id, name FROM tags WHERE id = %s",
            (tag_id,)
        )
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return Tag(*result) if result else None
    
@staticmethod
def get_note_tags(note_id: int) -> List[Tag]:
    """Получает все теги привязанные к заметке"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT t.id, t.user_id, t.name 
        FROM tags t
        JOIN note_tags nt ON t.id = nt.tag_id
        WHERE nt.note_id = %s
    """, (note_id,))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return [Tag(*row) for row in results]

class TagRepository:
    @staticmethod
    def get_or_create(user_id: int, name: str) -> Tag:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO tags (user_id, name) VALUES (%s, %s) "
            "ON CONFLICT (user_id, name) DO UPDATE SET name = EXCLUDED.name "
            "RETURNING id, user_id, name",
            (user_id, name)
        )
        result = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        return Tag(*result) if result else None

    @staticmethod
    def add_to_note(note_id: int, tag_id: int):
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO note_tags (note_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (note_id, tag_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_user_tags(user_id: int) -> List[Tag]:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, user_id, name FROM tags WHERE user_id = %s ORDER BY name",
            (user_id,)
        )
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [Tag(*row) for row in results]

    # ДОБАВЛЯЕМ НОВЫЙ МЕТОД
    @staticmethod
    def get_by_id(tag_id: int) -> Optional[Tag]:
        """Получает тег по ID"""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, user_id, name FROM tags WHERE id = %s",
            (tag_id,)
        )
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return Tag(*result) if result else None

    @staticmethod
    def get_note_tags(note_id: int) -> List[Tag]:
        """Получает все теги привязанные к заметке"""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT t.id, t.user_id, t.name 
            FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = %s
        """, (note_id,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [Tag(*row) for row in results]