from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.note_service import NoteService
from database.repository import NoteRepository
from utils.states import CreateNoteStates
from utils.helpers import format_note, format_notes_list
from utils.states import EditNoteStates
from services.tag_service import TagService
from utils.states import CreateNoteStates, EditNoteStates 
from keyboards.main_menu import get_main_menu
from keyboards.note_actions import get_note_actions

router = Router()

@router.message(F.text == "📝 Создать заметку")
async def create_note_start(message: Message, state: FSMContext):
    await state.set_state(CreateNoteStates.waiting_for_title)
    await message.answer("Введите заголовок заметки:")

@router.message(CreateNoteStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateNoteStates.waiting_for_content)
    await message.answer("Введите содержание заметки (или 'пропустить' для пустого):")

@router.message(CreateNoteStates.waiting_for_content)
async def process_content(message: Message, state: FSMContext):
    content = None if message.text.lower() == 'пропустить' else message.text
    data = await state.get_data()
    
    note = NoteService.create_note(
        user_id=message.from_user.id,
        title=data['title'],
        content=content
    )
    
    if note:
        await message.answer(
            f"✅ Заметка создана!\n\n{format_note(note)}",
            reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
        )
        
        # Предлагаем добавить теги
        from services.tag_service import TagService
        tags = TagService.get_user_tags(message.from_user.id)
        if tags:
            from keyboards.tags_keyboard import get_tags_keyboard
            await message.answer(
                "🏷 Хотите добавить теги к заметке?",
                reply_markup=get_tags_keyboard(tags, note.id)
            )
    else:
        await message.answer("❌ Ошибка при создании заметки")
    
    await state.clear()

@router.message(F.text == "📋 Мои заметки")
async def show_all_notes(message: Message):
    notes = NoteService.get_user_notes(message.from_user.id)
    
    if not notes:
        await message.answer("📭 У вас пока нет заметок.")
        return
    
    await message.answer(format_notes_list(notes))
    
    # Показываем заметки с правильными кнопками
    for note in notes[:5]:
        await message.answer(
            format_note(note),
            reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
        )
    
    if len(notes) > 5:
        await message.answer(f"📄 Показано 5 из {len(notes)} заметок")

@router.message(F.text == "✅ Выполненные")
async def show_completed_notes(message: Message):
    notes = NoteService.get_user_notes(message.from_user.id, status="completed")
    
    if not notes:
        await message.answer("✅ Нет выполненных заметок.")
        return
    
    for note in notes:
        await message.answer(
            format_note(note),
            reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
        )

@router.message(F.text == "📌 Закрепленные")
async def show_pinned_notes(message: Message):
    notes = NoteService.get_user_notes(message.from_user.id)
    pinned_notes = [note for note in notes if note.is_pinned]
    
    if not pinned_notes:
        await message.answer("📌 Нет закрепленных заметок.")
        return
    
    for note in pinned_notes:
        await message.answer(
            format_note(note),
            reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
        )

@router.callback_query(F.data.startswith("complete_"))
async def complete_note(callback: CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    
    # Получаем текущий статус заметки
    note = NoteRepository.get_by_id(note_id)
    if not note:
        await callback.answer("❌ Заметка не найдена")
        return
    
    # Меняем статус
    new_status = "completed" if note.status == "active" else "active"
    if new_status == "completed":
        NoteService.complete_note(note_id)
    else:
        NoteService.update_note_status(note_id, "active")
    
    # Обновляем сообщение с новыми кнопками
    text = callback.message.text
    if new_status == "completed":
        text = text.replace("📝", "✅") if "📝" in text else "✅ " + text
    else:
        text = text.replace("✅", "📝") if "✅" in text else "📝 " + text
    
    await callback.message.edit_text(
        text,
        reply_markup=get_note_actions(note_id, new_status, note.is_pinned)
    )
    
    status_text = "выполнена" if new_status == "completed" else "возвращена в работу"
    await callback.answer(f"✅ Заметка {status_text}!")

@router.callback_query(F.data.startswith("pin_"))
async def pin_note(callback: CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    
    # Получаем текущее состояние заметки
    note = NoteRepository.get_by_id(note_id)
    if not note:
        await callback.answer("❌ Заметка не найдена")
        return
    
    is_pinned = NoteService.toggle_pin(note_id)
    
    # Обновляем сообщение с новыми кнопками
    text = callback.message.text
    if is_pinned and "📌" not in text:
        text = "📌 " + text
    elif not is_pinned and text.startswith("📌 "):
        text = text[3:]
    
    await callback.message.edit_text(
        text,
        reply_markup=get_note_actions(note_id, note.status, is_pinned)
    )
    
    status = "закреплена" if is_pinned else "откреплена"
    await callback.answer(f"📌 Заметка {status}!")

@router.callback_query(F.data.startswith("delete_"))
async def delete_note(callback: CallbackQuery):
    note_id = int(callback.data.split("_")[1])
    NoteService.delete_note(note_id)
    await callback.message.delete()
    await callback.answer("🗑 Заметка удалена!")
    
@router.callback_query(F.data.startswith("edit_"))
async def edit_note_start(callback: CallbackQuery):
    """Показывает меню редактирования заметки"""
    note_id = int(callback.data.split("_")[1])
    
    from keyboards.note_actions import get_edit_actions
    
    await callback.message.edit_text(
        "✏️ Что вы хотите отредактировать?",
        reply_markup=get_edit_actions(note_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_title_"))
async def edit_note_title_start(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс редактирования заголовка"""
    note_id = int(callback.data.split("_")[2])
    
    # Сохраняем note_id в состоянии
    await state.update_data(note_id=note_id)
    await state.set_state(EditNoteStates.waiting_for_title)
    
    # Получаем текущий заголовок
    note = NoteService.get_note_by_id(note_id)
    current_title = note.title if note else ""
    
    await callback.message.answer(
        f"📝 Введите новый заголовок для заметки:\n\n"
        f"<i>Текущий заголовок: {current_title}</i>"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_content_"))
async def edit_note_content_start(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс редактирования содержания"""
    note_id = int(callback.data.split("_")[2])
    
    # Сохраняем note_id в состоянии
    await state.update_data(note_id=note_id)
    await state.set_state(EditNoteStates.waiting_for_content)
    
    # Получаем текущее содержание
    note = NoteService.get_note_by_id(note_id)
    current_content = note.content if note and note.content else "Без описания"
    
    await callback.message.answer(
        f"📄 Введите новое содержание для заметки:\n\n"
        f"<i>Текущее содержание: {current_content}</i>"
    )
    await callback.answer()

@router.message(EditNoteStates.waiting_for_title)
async def process_edit_title(message: Message, state: FSMContext):
    """Обрабатывает новый заголовок"""
    data = await state.get_data()
    note_id = data['note_id']
    new_title = message.text.strip()
    
    if not new_title:
        await message.answer("❌ Заголовок не может быть пустым. Попробуйте еще раз:")
        return
    
    # Обновляем заголовок
    NoteService.update_note_title(note_id, new_title)
    
    # Получаем обновленную заметку
    note = NoteService.get_note_by_id(note_id)
    tags = TagService.get_note_tags(note_id)
    tag_names = [tag.name for tag in tags] if tags else []
    
    await message.answer(
        f"✅ Заголовок обновлен!\n\n{format_note(note, tag_names)}",
        reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
    )
    
    await state.clear()

@router.message(EditNoteStates.waiting_for_content)
async def process_edit_content(message: Message, state: FSMContext):
    """Обрабатывает новое содержание"""
    data = await state.get_data()
    note_id = data['note_id']
    new_content = message.text.strip()
    
    # Обновляем содержание (может быть пустым)
    NoteService.update_note_content(note_id, new_content if new_content else None)
    
    # Получаем обновленную заметку
    note = NoteService.get_note_by_id(note_id)
    tags = TagService.get_note_tags(note_id)
    tag_names = [tag.name for tag in tags] if tags else []
    
    await message.answer(
        f"✅ Содержание обновлено!\n\n{format_note(note, tag_names)}",
        reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
    )
    
    await state.clear()

@router.callback_query(F.data.startswith("back_to_note_"))
async def back_to_note(callback: CallbackQuery):
    """Возвращает к просмотру заметки"""
    note_id = int(callback.data.split("_")[3])
    
    # Получаем заметку
    note = NoteService.get_note_by_id(note_id)
    if not note:
        await callback.answer("❌ Заметка не найдена")
        return
    
    tags = TagService.get_note_tags(note_id)
    tag_names = [tag.name for tag in tags] if tags else []
    
    await callback.message.edit_text(
        format_note(note, tag_names),
        reply_markup=get_note_actions(note.id, note.status, note.is_pinned)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("edit_tags_"))
async def edit_note_tags(callback: CallbackQuery):
    """Редактирование тегов заметки"""
    note_id = int(callback.data.split("_")[2])
    
    # Получаем теги пользователя
    tags = TagService.get_user_tags(callback.from_user.id)
    
    if not tags:
        await callback.answer("❌ У вас пока нет тегов")
        return
    
    from keyboards.tags_keyboard import get_tags_keyboard
    await callback.message.edit_text(
        "🏷 Выберите теги для добавления к заметке:",
        reply_markup=get_tags_keyboard(tags, note_id)
    )
    await callback.answer()