### **8. `main.py`** - Main Entry Point python
#!/usr/bin/env python3
import os
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point"""
    logger.info("🚀 Starting InstaVoice Bot...")
    
    # Import after logging setup
    from config import Config
    from database import db
    from bot import bot, dp, on_startup, on_shutdown
    
    try:
        # Validate config
        Config.validate()
        logger.info("✅ Configuration validated")
        
        # Connect to database
        await db.connect()
        logger.info("✅ Database connected")
        
        # Setup startup
        await on_startup()
        
        # Start polling
        logger.info("🤖 Bot is now running...")
        await dp.start_polling()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
    finally:
        await on_shutdown()
        await db.disconnect()
        logger.info("👋 Bot stopped")

if __name__ == "__main__":
    # Create required directories
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp_voices", exist_ok=True)
    
    # Run bot
    asyncio.run(main())
