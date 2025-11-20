from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.tag_service import TagService
from services.note_service import NoteService
from utils.states import TagStates
from keyboards.tags_keyboard import get_tags_keyboard
from utils.helpers import format_note
from keyboards.note_actions import get_note_actions

router = Router()

@router.message(F.text == "🏷 Мои теги")
async def show_user_tags(message: Message):
    tags = TagService.get_user_tags(message.from_user.id)
    
    if not tags:
        await message.answer("🏷 У вас пока нет тегов.")
        return
    
    tag_list = "\n".join([f"• #{tag.name}" for tag in tags])
    await message.answer(
        f"🏷 Ваши теги:\n\n{tag_list}\n\n"
        "Нажмите на тег для фильтрации заметок:",
        reply_markup=get_tags_keyboard(tags)
    )

@router.callback_query(F.data.startswith("filter_tag_"))
async def filter_by_tag(callback: CallbackQuery):
    tag_name = callback.data.split("_")[2]
    notes = NoteService.get_user_notes(callback.from_user.id, tag=tag_name)
    
    if not notes:
        await callback.answer(f"❌ Нет заметок с тегом #{tag_name}")
        return
    
    await callback.message.edit_text(f"📋 Заметки с тегом #{tag_name}:")
    
    for note in notes[:10]:
        await callback.message.answer(
            format_note(note),
            reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
        )
    
    await callback.answer(f"📋 Показаны заметки с тегом #{tag_name}")

@router.callback_query(F.data.startswith("add_tag_"))
async def add_existing_tag_to_note(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        tag_id = int(parts[2])
        note_id = int(parts[3])
        
        print(f"🔧 Добавляем тег {tag_id} к заметке {note_id}")  # Дебаг
        
        # Получаем тег по ID
        tag = TagService.get_by_id(tag_id)
        
        if tag:
            # Добавляем тег к заметке
            TagService.add_tag_to_note(callback.from_user.id, note_id, tag.name)
            
            # ОБНОВЛЯЕМ СООБЩЕНИЕ С ЗАМЕТКОЙ, ЧТОБЫ ПОКАЗАТЬ НОВЫЕ ТЕГИ
            from services.note_service import NoteService
            note = NoteService.get_note_by_id(note_id)
            from utils.helpers import format_note
            from keyboards.note_actions import get_note_actions
            
            await callback.message.edit_text(
                format_note(note),
                reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
            )
            
            await callback.answer(f"✅ Тег #{tag.name} добавлен к заметке")
        else:
            await callback.answer("❌ Тег не найден")
            
    except Exception as e:
        print(f"❌ Ошибка добавления тега: {e}")
        await callback.answer("❌ Ошибка добавления тега")

@router.callback_query(F.data.startswith("new_tag_"))
async def create_new_tag_start(callback: CallbackQuery, state: FSMContext):
    """Начинаем процесс создания нового тега"""
    note_id = int(callback.data.split("_")[2])
    
    # Сохраняем note_id в состоянии
    await state.update_data(note_id=note_id)
    await state.set_state(TagStates.waiting_for_tag_name)
    
    await callback.message.answer(
        "🏷 Введите название нового тега (только буквы, цифры и подчеркивание):"
    )
    await callback.answer()

@router.message(TagStates.waiting_for_tag_name)
async def process_new_tag_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названия тега"""
    tag_name = message.text.strip()
    
    # Простая валидация
    if not tag_name or len(tag_name) > 20:
        await message.answer("❌ Название тега должно быть от 1 до 20 символов. Попробуйте еще раз:")
        return
    
    # Получаем note_id из состояния
    data = await state.get_data()
    note_id = data['note_id']
    
    try:
        # Создаем тег и добавляем к заметке
        tag = TagService.create_tag(message.from_user.id, tag_name)
        if tag:
            TagService.add_tag_to_note(message.from_user.id, note_id, tag_name)
            await message.answer(f"✅ Тег #{tag_name} создан и добавлен к заметке!")
        else:
            await message.answer("❌ Ошибка создания тега")
    
    except Exception as e:
        await message.answer("❌ Ошибка при создании тега. Возможно, тег с таким названием уже существует.")
    
    await state.clear()

@router.callback_query(F.data == "back_to_notes")
async def back_to_notes(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Возврат к заметкам")