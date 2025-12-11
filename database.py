# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.errors import DuplicateKeyError, OperationFailure
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB and create indexes with robust fallbacks."""
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # users: unique user_id
        await self.db.users.create_index("user_id", unique=True)

        # groups: prefer strict unique index, but be tolerant to messy existing data
        try:
            await self.db.groups.create_index("chat_id", unique=True)
            logger.info("Created strict unique index on groups.chat_id")
        except DuplicateKeyError as e:
            # DuplicateKey: likely multiple documents have chat_id == null
            logger.warning("Strict unique index failed due to duplicate keys: %s", e)
            # Attempt to unset explicit null values so sparse index will ignore them
            try:
                res = await self.db.groups.update_many({"chat_id": None}, {"$unset": {"chat_id": ""}})
                logger.info("Unset chat_id on %d documents where chat_id was null", res.modified_count)
                # Now create a sparse unique index (ignores documents missing the field)
                await self.db.groups.create_index("chat_id", unique=True, sparse=True)
                logger.info("Created sparse unique index on groups.chat_id after unsetting nulls")
            except Exception as e2:
                logger.exception("Failed to create sparse unique index after unsetting nulls: %s", e2)
                # As a last resort try a partial index that only indexes numeric chat_id values.
                # Some Mongo servers reject $ne or $not expressions in partialFilterExpression.
                try:
                    # Index only documents where chat_id is numeric (int/long/double)
                    await self.db.groups.create_index(
                        [("chat_id", 1)],
                        unique=True,
                        partialFilterExpression={"chat_id": {"$type": ["int", "long", "double"]}}
                    )
                    logger.info("Created partial unique index on numeric chat_id values")
                except Exception as e3:
                    logger.exception("Failed to create partial unique index as last resort: %s", e3)
                    raise e3 from e2

        except OperationFailure as oe:
            # OperationFailure can mean the server rejected partial expressions or other index options.
            logger.warning("Creating strict unique index failed (OperationFailure): %s", oe)
            # Try to create sparse unique index directly (after unsetting nulls)
            try:
                res = await self.db.groups.update_many({"chat_id": None}, {"$unset": {"chat_id": ""}})
                logger.info("Unset chat_id on %d documents where chat_id was null", res.modified_count)
                await self.db.groups.create_index("chat_id", unique=True, sparse=True)
                logger.info("Created sparse unique index on groups.chat_id after OperationFailure")
            except Exception as e2:
                logger.exception("Failed to recover from OperationFailure when creating groups.chat_id index: %s", e2)
                # Try partial index by numeric type
                try:
                    await self.db.groups.create_index(
                        [("chat_id", 1)],
                        unique=True,
                        partialFilterExpression={"chat_id": {"$type": ["int", "long", "double"]}}
                    )
                    logger.info("Created partial unique index on numeric chat_id values (fallback)")
                except Exception as e3:
                    logger.exception("Final fallback index creation also failed: %s", e3)
                    raise e3 from e2

        # voices: compound index for fast queries by user and time
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
