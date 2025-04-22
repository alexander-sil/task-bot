from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_task_id_to_delete = State()
    waiting_for_task_id_to_edit = State()
    waiting_for_new_title = State()
    waiting_for_new_description = State()
    waiting_for_task_id_to_comment = State()
    waiting_for_comment = State()
