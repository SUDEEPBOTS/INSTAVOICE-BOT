"""
FSM States for the bot
"""
from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_gc_link = State()
    waiting_for_session = State()
    waiting_for_filter = State()
