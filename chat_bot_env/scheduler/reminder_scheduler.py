import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

from database.repository import ReminderRepository
from database.connection import get_connection

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        # Проверяем напоминания каждую минуту
        self.scheduler.add_job(
            self.check_reminders,
            'interval',
            minutes=1,
            id='check_reminders'
        )
        
        # Очистка старых напоминаний каждый день
        self.scheduler.add_job(
            self.cleanup_old_reminders,
            'cron',
            hour=3,
            minute=0,
            id='cleanup_reminders'
        )
        
        self.scheduler.start()
        print("✅ Планировщик напоминаний запущен")
    
    async def check_reminders(self):
        try:
            reminders = ReminderRepository.get_pending_reminders()
            
            for reminder in reminders:
                reminder_id, note_id, reminder_time, reminder_type, is_active, created_at, title, content, user_id = reminder
                
                # Отправляем напоминание
                await self.send_reminder(user_id, note_id, title, content, reminder_type)
                
                # Обрабатываем повторяющиеся напоминания
                if reminder_type != 'once':
                    await self.reschedule_repeating_reminder(reminder_id, reminder_type)
                else:
                    await self.deactivate_reminder(reminder_id)
                    
        except Exception as e:
            print(f"❌ Ошибка в планировщике: {e}")
    
    async def send_reminder(self, user_id: int, note_id: int, title: str, content: str, reminder_type: str):
        try:
            type_icon = {
                'once': '⏰',
                'daily': '🔄',
                'weekly': '📅',
                'monthly': '📆'
            }.get(reminder_type, '⏰')
            
            message_text = (
                f"{type_icon} <b>Напоминание</b>\n\n"
                f"<b>{title}</b>\n"
                f"{content or 'Без описания'}"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message_text
            )
            print(f"✅ Напоминание отправлено пользователю {user_id}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки напоминания: {e}")
    
    async def reschedule_repeating_reminder(self, reminder_id: int, reminder_type: str):
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            new_time = datetime.now()
            if reminder_type == 'daily':
                new_time += timedelta(days=1)
            elif reminder_type == 'weekly':
                new_time += timedelta(weeks=1)
            elif reminder_type == 'monthly':
                new_time += timedelta(days=30)
            
            cur.execute(
                "UPDATE reminders SET reminder_time = %s WHERE id = %s",
                (new_time, reminder_id)
            )
            conn.commit()
            
        except Exception as e:
            print(f"❌ Ошибка переноса напоминания: {e}")
        finally:
            cur.close()
            conn.close()
    
    async def deactivate_reminder(self, reminder_id: int):
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "UPDATE reminders SET is_active = FALSE WHERE id = %s",
                (reminder_id,)
            )
            conn.commit()
            
        except Exception as e:
            print(f"❌ Ошибка деактивации напоминания: {e}")
        finally:
            cur.close()
            conn.close()
    
    async def cleanup_old_reminders(self):
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            # Удаляем старые неактивные напоминания (старше 30 дней)
            cur.execute(
                "DELETE FROM reminders WHERE is_active = FALSE AND created_at < NOW() - INTERVAL '30 days'"
            )
            conn.commit()
            print("✅ Старые напоминания очищены")
            
        except Exception as e:
            print(f"❌ Ошибка очистки напоминаний: {e}")
        finally:
            cur.close()
            conn.close()
    
    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("✅ Планировщик остановлен")

def setup_scheduler(bot):
    return ReminderScheduler(bot)