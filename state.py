from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    STATE_SCORE = State()
    STATE_TIME = State()