from aiogram.fsm.state import State, StatesGroup

class TaskStates(StatesGroup):
    title = State()
    due = State()
    category = State()


class CategoryStates(StatesGroup):
    title = State()