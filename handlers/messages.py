# handlers/messages.py
"""
Message handlers (Aiogram v2)
"""
from aiogram import types
from aiogram.dispatcher import FSMContext

from src.voice_service import VoiceService
from database import db
from bot import dp  # same global dispatcher

voice_service = VoiceService()


@dp.message_handler(content_types=types.ContentType.VOICE, chat_type=types.ChatType.PRIVATE)
async def handle_voice(message: types.Message):
    """Handle voice messages"""
    processing_msg = await message.reply("🔮 Processing your voice...")

    user_id = message.from_user.id
    voice_file_id = message.voice.file_id

    # Process voice
    success, result = await voice_service.process_voice(user_id, voice_file_id, message.bot)

    await processing_msg.edit_text(result)


@dp.message_handler(content_types=types.ContentType.TEXT, chat_type=types.ChatType.PRIVATE)
async def handle_text(message: types.Message):
    """Handle text messages"""
    # Ignore if it's a command
    if message.text.startswith('/'):
        return

    await message.reply(
        "💡 Send me a voice note and I'll play it in deep voice!\n\n"
        "Use /help for commands."
    )
