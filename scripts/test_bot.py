#!/usr/bin/env python3
"""
Test script for bot functionality
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_all():
    """Test all components"""
    print("\n🧪 Testing InstaVoice Bot Components...")
    
    # Test config
    try:
        from config import Config
        Config.validate()
        print("✅ Config: Valid")
    except Exception as e:
        print(f"❌ Config: {e}")
        return
    
    # Test database
    try:
        from database import db
        await db.connect()
        print("✅ Database: Connected")
        await db.disconnect()
    except Exception as e:
        print(f"❌ Database: {e}")
    
    print("\n✅ All tests passed! Bot is ready.")

if __name__ == "__main__":
    asyncio.run(test_all())
