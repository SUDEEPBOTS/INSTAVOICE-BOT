"""
Handlers package
"""
from .commands import dp as commands_dp
from .messages import dp as messages_dp
from .callbacks import dp as callbacks_dp

__all__ = ['commands_dp', 'messages_dp', 'callbacks_dp']
