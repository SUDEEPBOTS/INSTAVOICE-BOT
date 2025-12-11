"""
Bot initialization utilities
"""
from aiogram import Dispatcher

def setup_bot(dp: Dispatcher):
    """Setup all bot handlers"""
    from handlers import commands, messages, callbacks
    
    # Include routers
    dp.include_router(commands.dp)
    dp.include_router(messages.dp)
    dp.include_router(callbacks.dp)
    
    return dp
