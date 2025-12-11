"""
Callback query handlers
"""
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from database import db

dp = Dispatcher()

@dp.callback_query_handler(lambda c: c.data.startswith('filter_'))
async def handle_filter_callback(callback_query: types.CallbackQuery):
    """Handle filter selection"""
    filter_type = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    await db.set_filter(user_id, filter_type)
    
    filter_names = {
        "deep": "🎤 Deep Voice",
        "robot": "🤖 Robot",
        "radio": "📻 Radio",
        "echo": "🌌 Echo",
        "bass": "🎵 Bass Boost"
    }
    
    await callback_query.message.edit_text(
        f"✅ Filter updated to: <b>{filter_names.get(filter_type, 'Deep')}</b>\n\n"
        f"Now send a voice note to test!"
    )
    await callback_query.answer()
