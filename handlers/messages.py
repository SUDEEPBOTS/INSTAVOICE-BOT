# handlers/messages.py
"""
Message handlers (aiogram v3, Router-based)
"""
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.voice_service import VoiceService
from database import db

router = Router()
voice_service = VoiceService()


def _is_private(chat: types.Chat) -> bool:
    try:
        return chat.type == types.ChatType.PRIVATE
    except Exception:
        return False


@router.message(lambda message: message.content_type == types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    """Handle voice messages (private only)"""
    if not _is_private(message.chat):
        return

    processing_msg = await message.reply("🔮 Processing your voice...")

    user_id = message.from_user.id
    voice_file_id = message.voice.file_id

    # Process voice
    # voice_service.process_voice should be async and accept (user_id, file_id, bot)
    success, result = await voice_service.process_voice(user_id, voice_file_id, message.bot)

    await processing_msg.edit_text(result)


@router.message(lambda message: message.content_type == types.ContentType.TEXT)
async def handle_text(message: types.Message):
    """Handle text messages (private only)"""
    if not _is_private(message.chat):
        return

    # Ignore if it's a command
    text = (message.text or "").strip()
    if text.startswith("/"):
        return

    await message.reply(
        "💡 Send me a voice note and I'll play it in deep voice!\n\n"
        "Use /help for commands."
    )


# Export as `dp` so bot.py can import: from handlers.messages import dp as messages_dp
dp = router
