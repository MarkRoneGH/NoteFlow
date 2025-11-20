from aiogram.fsm.state import State, StatesGroup

class CreateNoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tags = State()

class EditNoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tags = State()

class SearchStates(StatesGroup):
    waiting_for_query = State()

# ДОБАВЛЯЕМ НОВЫЕ СОСТОЯНИЯ ДЛЯ ТЕГОВ
class TagStates(StatesGroup):
    waiting_for_tag_name = State()