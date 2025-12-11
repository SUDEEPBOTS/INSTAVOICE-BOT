from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Config

# Initialize
bot = Bot(token=Config.BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Import handlers
from handlers.commands import dp as commands_dp
from handlers.messages import dp as messages_dp
from handlers.callbacks import dp as callbacks_dp

# Include routers
dp.include_router(commands_dp)
dp.include_router(messages_dp)
dp.include_router(callbacks_dp)

# Startup/shutdown
async def on_startup():
    """Bot startup actions"""
    me = await bot.get_me()
    print("\n" + "="*50)
    print(f"🎤 InstaVoice Bot Started!")
    print(f"🤖 Bot: @{me.username}")
    print(f"👤 Owner: {Config.OWNER_ID}")
    print("="*50)
    
    # Send to owner
    try:
        await bot.send_message(
            Config.OWNER_ID,
            f"✅ Bot started successfully!\n\n"
            f"Username: @{me.username}\n"
            f"ID: {me.id}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except:
        pass

async def on_shutdown():
    """Bot shutdown actions"""
    print("\n👋 Bot is shutting down...")
    
    # Cleanup
    from utils.userbot_manager import userbot_manager
    await userbot_manager.stop_all()
