from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.reminder_service import ReminderService
from keyboards.reminder_keyboard import get_reminder_keyboard

router = Router()

@router.callback_query(F.data.startswith("remind_"))
async def show_reminder_options(callback: CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    
    await callback.message.answer(
        "⏰ Выберите время напоминания:",
        reply_markup=get_reminder_keyboard(note_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reminder_"))
async def set_time_reminder(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        minutes = int(parts[1])
        note_id = int(parts[2])
        
        reminder = ReminderService.create_reminder(note_id, minutes=minutes)
        
        if reminder:
            time_text = {
                10: "10 минут", 60: "1 час", 180: "3 часа", 1440: "1 день"
            }.get(minutes, f"{minutes} минут")
            
            await callback.answer(f"⏰ Напоминание установлено на {time_text}!")
        else:
            await callback.answer("❌ Ошибка установки напоминания")
            
    except Exception as e:
        await callback.answer("❌ Ошибка установки напоминания")

@router.callback_query(F.data.startswith("repeat_"))
async def set_repeat_reminder(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        reminder_type = parts[1]  # daily, weekly
        note_id = int(parts[2])
        
        reminder = ReminderService.create_reminder(note_id, reminder_type=reminder_type)
        
        if reminder:
            type_text = {
                'daily': 'ежедневно', 'weekly': 'еженедельно', 'monthly': 'ежемесячно'
            }.get(reminder_type, reminder_type)
            
            await callback.answer(f"⏰ Повторяющееся напоминание установлено ({type_text})!")
        else:
            await callback.answer("❌ Ошибка установки напоминания")
            
    except Exception as e:
        await callback.answer("❌ Ошибка установки напоминания")