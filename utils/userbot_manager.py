"""
UserBot manager using Telethon
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.phone import JoinGroupCallRequest
import asyncio
from typing import Optional, Dict
from config import Config

class UserBotManager:
    def __init__(self):
        self.clients: Dict[int, TelegramClient] = {}
        self.active_chats: Dict[int, int] = {}
        self.lock = asyncio.Lock()
        
    async def start_client(self, user_id: int) -> Optional[TelegramClient]:
        """Start Telethon client"""
        async with self.lock:
            if user_id in self.clients:
                return self.clients[user_id]
                
            try:
                # Use session from .env
                client = TelegramClient(
                    StringSession(Config.SESSION_STRING),
                    Config.API_ID,
                    Config.HASH
                )
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    print(f"UserBot not authorized for {user_id}")
                    await client.disconnect()
                    return None
                    
                me = await client.get_me()
                print(f"UserBot started: @{me.username}")
                
                self.clients[user_id] = client
                return client
                
            except Exception as e:
                print(f"Error starting UserBot: {e}")
                return None
                
    async def join_voice_chat(self, user_id: int, chat_id: int) -> bool:
        """Join voice chat"""
        try:
            client = await self.start_client(user_id)
            if not client:
                return False
                
            # Get chat
            chat = await client.get_entity(chat_id)
            
            # Join VC
            try:
                await client(JoinGroupCallRequest(
                    peer=chat,
                    muted=False,
                    video_stopped=False
                ))
            except:
                # Fallback method
                await client.send_message(chat, "!join")
                
            self.active_chats[user_id] = chat_id
            return True
            
        except Exception as e:
            print(f"Join VC error: {e}")
            return False
            
    async def leave_voice_chat(self, user_id: int) -> bool:
        """Leave voice chat"""
        try:
            if user_id not in self.active_chats:
                return True
                
            client = self.clients.get(user_id)
            if client:
                chat_id = self.active_chats[user_id]
                chat = await client.get_entity(chat_id)
                await client.send_message(chat, "!leave")
                
            del self.active_chats[user_id]
            return True
            
        except Exception as e:
            print(f"Leave VC error: {e}")
            return False
            
    async def play_audio(self, user_id: int, audio_path: str) -> bool:
        """Play audio in VC"""
        try:
            if user_id not in self.clients or user_id not in self.active_chats:
                return False
                
            client = self.clients[user_id]
            chat_id = self.active_chats[user_id]
            
            chat = await client.get_entity(chat_id)
            await client.send_file(chat, audio_path, voice_note=True)
            
            return True
            
        except Exception as e:
            print(f"Play audio error: {e}")
            return False
            
    async def stop_client(self, user_id: int):
        """Stop UserBot client"""
        async with self.lock:
            if user_id in self.clients:
                await self.leave_voice_chat(user_id)
                await self.clients[user_id].disconnect()
                del self.clients[user_id]
                
                if user_id in self.active_chats:
                    del self.active_chats[user_id]
                    
    async def stop_all(self):
        """Stop all UserBots"""
        tasks = [self.stop_client(uid) for uid in list(self.clients.keys())]
        await asyncio.gather(*tasks, return_exceptions=True)

# Global instance
userbot_manager = UserBotManager()
