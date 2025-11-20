from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.repository import UserRepository
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = UserRepository.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        "📝 Добро пожаловать в бот для заметок!\n\n"
        "Доступные команды:\n"
        "• /quick - быстрая заметка\n"
        "• /search - поиск по заметкам\n\n"
        "Используйте меню ниже для управления заметками:",
        reply_markup=get_main_menu()
    )
