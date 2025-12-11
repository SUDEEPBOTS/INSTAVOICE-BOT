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
        print(f"🔧 DEBUG: Starting UserBot for user {user_id}")
        
        async with self.lock:
            if user_id in self.clients:
                print(f"🔧 DEBUG: Client already exists")
                return self.clients[user_id]
                
            try:
                # CRITICAL FIX: Changed Config.HASH to Config.API_HASH
                print(f"🔧 DEBUG: Using API_ID={Config.API_ID}, API_HASH={Config.API_HASH[:10]}...")
                print(f"🔧 DEBUG: Session string length: {len(Config.SESSION_STRING)}")
                
                client = TelegramClient(
                    StringSession(Config.SESSION_STRING),
                    Config.API_ID,
                    Config.API_HASH  # ✅ FIXED THIS LINE
                )
                
                print("🔧 DEBUG: Connecting to Telegram...")
                await client.connect()
                
                if not await client.is_user_authorized():
                    print(f"❌ ERROR: UserBot not authorized. Check session string!")
                    await client.disconnect()
                    return None
                    
                me = await client.get_me()
                print(f"✅ SUCCESS: UserBot started as @{me.username} (ID: {me.id})")
                
                self.clients[user_id] = client
                return client
                
            except Exception as e:
                print(f"❌ ERROR starting UserBot: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
                
    async def join_voice_chat(self, user_id: int, chat_id: int) -> bool:
        """Join voice chat"""
        print(f"🔧 DEBUG: Joining VC - user={user_id}, chat={chat_id}")
        
        try:
            client = await self.start_client(user_id)
            if not client:
                print(f"❌ ERROR: No client to join VC")
                return False
                
            print(f"🔧 DEBUG: Getting chat entity...")
            chat = await client.get_entity(chat_id)
            print(f"🔧 DEBUG: Chat found: {chat.title}")
            
            # Join VC
            try:
                print("🔧 DEBUG: Trying JoinGroupCallRequest...")
                await client(JoinGroupCallRequest(
                    peer=chat,
                    muted=False,
                    video_stopped=False
                ))
                print("✅ SUCCESS: Joined VC via API")
            except Exception as e:
                print(f"⚠️ WARNING: API method failed: {e}. Using fallback...")
                # Fallback method
                await client.send_message(chat, "!join")
                print("✅ SUCCESS: Sent !join command")
                
            self.active_chats[user_id] = chat_id
            print(f"✅ SUCCESS: User {user_id} joined VC {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR joining VC: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
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
                print(f"✅ Left VC for user {user_id}")
                
            del self.active_chats[user_id]
            return True
            
        except Exception as e:
            print(f"Leave VC error: {e}")
            return False
            
    async def play_audio(self, user_id: int, audio_path: str) -> bool:
        """Play audio in VC"""
        try:
            if user_id not in self.clients or user_id not in self.active_chats:
                print(f"❌ ERROR: User {user_id} not ready for audio")
                return False
                
            client = self.clients[user_id]
            chat_id = self.active_chats[user_id]
            
            chat = await client.get_entity(chat_id)
            print(f"🔧 DEBUG: Playing audio in {chat.title}")
            await client.send_file(chat, audio_path, voice_note=True)
            
            print(f"✅ SUCCESS: Audio played")
            return True
            
        except Exception as e:
            print(f"❌ ERROR playing audio: {e}")
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
                print(f"✅ Stopped UserBot for user {user_id}")
                    
    async def stop_all(self):
        """Stop all UserBots"""
        tasks = [self.stop_client(uid) for uid in list(self.clients.keys())]
        await asyncio.gather(*tasks, return_exceptions=True)

# Global instance
userbot_manager = UserBotManager()
