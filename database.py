from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Create indexes
        await self.db.users.create_index("user_id", unique=True)
        await self.db.groups.create_index("chat_id", unique=True)
        await self.db.voices.create_index([("user_id", 1), ("timestamp", -1)])
        
        return True
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            
    # User methods
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "is_active": False,
            "voice_filter": "deep",
            "chat_id": None,
            "group_title": None,
            "created_at": datetime.now(),
            "last_seen": datetime.now()
        }
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
        return user_data
        
    async def get_user(self, user_id: int):
        return await self.db.users.find_one({"user_id": user_id})
        
    async def update_user(self, user_id: int, data: Dict):
        data["last_seen"] = datetime.now()
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": data}
        )
        
    async def set_active(self, user_id: int, active: bool = True):
        await self.update_user(user_id, {"is_active": active})
        
    async def set_filter(self, user_id: int, filter_name: str):
        await self.update_user(user_id, {"voice_filter": filter_name})
        
    async def set_group(self, user_id: int, chat_id: int, title: str, username: str = None):
        await self.update_user(user_id, {
            "chat_id": chat_id,
            "group_title": title,
            "group_username": username
        })
        
        # Also save to groups collection
        await self.db.groups.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "chat_id": chat_id,
                    "title": title,
                    "username": username,
                    "owner_id": user_id,
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
        
    # Stats
    async def add_voice_record(self, user_id: int, duration: int, filter_used: str):
        await self.db.voices.insert_one({
            "user_id": user_id,
            "duration": duration,
            "filter": filter_used,
            "timestamp": datetime.now()
        })
        
    async def get_user_stats(self, user_id: int):
        count = await self.db.voices.count_documents({"user_id": user_id})
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$filter",
                "count": {"$sum": 1}
            }}
        ]
        
        filter_stats = {}
        async for doc in self.db.voices.aggregate(pipeline):
            filter_stats[doc["_id"]] = doc["count"]
            
        return {
            "total_voices": count,
            "filter_stats": filter_stats
        }
        
    async def get_all_users(self):
        cursor = self.db.users.find({})
        return await cursor.to_list(length=None)
        
    async def get_active_users(self):
        cursor = self.db.users.find({"is_active": True})
        return await cursor.to_list(length=None)

# Global instance
db = Database()
