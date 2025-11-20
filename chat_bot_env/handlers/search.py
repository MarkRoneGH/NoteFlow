from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import SearchStates
from services.note_service import NoteService
from utils.helpers import format_note
from keyboards.note_actions import get_note_actions

router = Router()

@router.message(Command("search"))
@router.message(F.text == "🔍 Поиск")
async def search_start(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer("🔍 Введите поисковый запрос:")

@router.message(SearchStates.waiting_for_query)
async def process_search(message: Message, state: FSMContext):
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer("❌ Запрос должен содержать минимум 2 символа")
        return
    
    notes = NoteService.search_notes(message.from_user.id, query)
    
    if not notes:
        await message.answer("🔍 По вашему запросу ничего не найдено")
        await state.clear()
        return
    
    await message.answer(f"🔍 Найдено заметок: {len(notes)}")
    
    for note in notes[:10]:  # Ограничиваем показ
        await message.answer(
            format_note(note),
            reply_markup=get_note_actions(note.id)
        )
    
    await state.clear()