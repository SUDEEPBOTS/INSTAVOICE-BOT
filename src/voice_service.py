"""
Voice processing service
"""
import os
import asyncio
from typing import Tuple
from config import Config
from utils.voice_processor import VoiceProcessor
from utils.userbot_manager import userbot_manager
from database import db

class VoiceService:
    def __init__(self):
        self.processor = VoiceProcessor()
        
    async def process_voice(self, user_id: int, voice_file_id: str, bot) -> Tuple[bool, str]:
        """Process and play voice"""
        try:
            # Check user
            user = await db.get_user(user_id)
            if not user or not user.get("is_active"):
                return False, "Bot is not active. Use /on first!"
                
            if not user.get("chat_id"):
                return False, "No group configured. Use /setgc first!"
                
            # Download voice
            voice_path = await self.processor.download_voice_note(voice_file_id, bot)
            if not voice_path:
                return False, "Failed to download voice!"
                
            # Process with user's filter
            filter_type = user.get("voice_filter", "deep")
            processed_path = await self.processor.convert_to_deep_voice(voice_path, filter_type)
            
            if not processed_path:
                return False, "Voice processing failed!"
                
            # Play in VC
            success = await userbot_manager.play_audio(user_id, processed_path)
            
            # Cleanup
            self.processor.cleanup_file(voice_path)
            if processed_path != voice_path:
                self.processor.cleanup_file(processed_path)
                
            if success:
                # Record stats
                await db.add_voice_record(user_id, 0, filter_type)
                return True, "✅ Voice played successfully!"
            else:
                return False, "Failed to play in voice chat!"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
