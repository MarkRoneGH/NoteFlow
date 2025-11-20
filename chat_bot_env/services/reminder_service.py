from database.repository import ReminderRepository
from database.models import Reminder
from datetime import datetime, timedelta

class ReminderService:
    @staticmethod
    def create_reminder(note_id: int, minutes: int = None, reminder_type: str = 'once') -> Reminder:
        if minutes:
            reminder_time = datetime.now() + timedelta(minutes=minutes)
        else:
            if reminder_type == 'daily':
                reminder_time = datetime.now() + timedelta(days=1)
            elif reminder_type == 'weekly':
                reminder_time = datetime.now() + timedelta(weeks=1)
            elif reminder_type == 'monthly':
                reminder_time = datetime.now() + timedelta(days=30)
            else:
                reminder_time = datetime.now() + timedelta(hours=1)
        
        return ReminderRepository.create(note_id, reminder_time, reminder_type)

    @staticmethod
    def get_pending_reminders():
        return ReminderRepository.get_pending_reminders()