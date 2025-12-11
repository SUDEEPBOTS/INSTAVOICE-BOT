"""
Command handlers (Aiogram v2)
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from database import db
from utils.userbot_manager import userbot_manager
from handlers.states import UserStates
from bot import dp  # ✅ yahi se main Dispatcher le rahe hain, naya nahi bana rahe


@dp.message_handler(Command("start"), chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    await db.add_user(user_id, username, first_name)

    welcome = f"""
🎤 <b>Welcome {first_name} to InstaVoice Bot!</b>

I convert your voice to Instagram/TikTok trending deep voice and play in voice chats!

<b>✨ Features:</b>
• Instagram style deep voice
• Multiple voice filters
• Auto join/leave VC
• High quality audio

<b>📱 Commands:</b>
/on - Activate bot & join VC
/off - Deactivate bot
/stop - Leave VC
/setgc - Set group chat
/filter - Change voice filter
/status - Check status
/debug - Debug UserBot status
/configcheck - Check config
/envtest - Test environment
/testuserbot - Test UserBot directly

<b>⚡ Quick Setup:</b>
1. Add me to group (make admin)
2. /setgc + group link
3. /on to activate
4. Send voice notes!

Made with ❤️ by @{username or 'InstaVoice'}
"""

    await message.reply(welcome)


@dp.message_handler(Command("on"), chat_type=types.ChatType.PRIVATE)
async def cmd_on(message: types.Message):
    """Activate bot"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await message.reply("Please use /start first!")
        return

    if not user.get("chat_id"):
        await message.reply("Please set group chat first using /setgc")
        return

    if user.get("is_active"):
        await message.reply("✅ Bot is already active!")
        return

    # Activate
    await db.set_active(user_id, True)

    # Join VC
    chat_id = user["chat_id"]
    success = await userbot_manager.join_voice_chat(user_id, chat_id)

    if success:
        await message.reply("✅ Bot activated and joined voice chat!")
    else:
        await message.reply("⚠️ Bot activated but couldn't join VC. Check permissions.")


@dp.message_handler(Command("off"), chat_type=types.ChatType.PRIVATE)
async def cmd_off(message: types.Message):
    """Deactivate bot"""
    user_id = message.from_user.id

    await userbot_manager.leave_voice_chat(user_id)
    await db.set_active(user_id, False)
    await userbot_manager.stop_client(user_id)

    await message.reply("✅ Bot deactivated!")


@dp.message_handler(Command("stop"), chat_type=types.ChatType.PRIVATE)
async def cmd_stop(message: types.Message):
    """Leave voice chat"""
    user_id = message.from_user.id

    await userbot_manager.leave_voice_chat(user_id)
    await db.set_active(user_id, False)

    await message.reply("✅ Left voice chat!")


@dp.message_handler(Command("setgc"), chat_type=types.ChatType.PRIVATE)
async def cmd_setgc(message: types.Message, state: FSMContext):
    """Set group chat"""
    await UserStates.waiting_for_gc_link.set()
    await message.reply("Please send your group link (e.g., https://t.me/groupname or @groupname):")


@dp.message_handler(state=UserStates.waiting_for_gc_link, chat_type=types.ChatType.PRIVATE)
async def process_gc_link(message: types.Message, state: FSMContext):
    """Process group link"""
    try:
        link = message.text.strip()
        user_id = message.from_user.id

        # Extract username
        if "t.me/" in link:
            username = link.split("t.me/")[-1].replace("@", "")
        elif link.startswith("@"):
            username = link[1:]
        else:
            await message.reply("Invalid format! Use: https://t.me/username or @username")
            await state.finish()
            return

        # Get chat info
        from bot import bot
        chat = await bot.get_chat(f"@{username}")

        # Save to DB
        await db.set_group(
            user_id=user_id,
            chat_id=chat.id,
            title=chat.title,
            username=username
        )

        await message.reply(
            f"✅ Group set successfully!\n\n"
            f"<b>Group:</b> {chat.title}\n"
            f"<b>ID:</b> <code>{chat.id}</code>\n\n"
            f"Now use /on to activate!"
        )

    except Exception as e:
        await message.reply(
            f"Error: {str(e)}\n\nMake sure:\n1. Bot is added to group\n2. Bot is admin"
        )
    finally:
        await state.finish()


@dp.message_handler(Command("filter"), chat_type=types.ChatType.PRIVATE)
async def cmd_filter(message: types.Message):
    """Change voice filter"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    filters = [
        ("🎤 Deep", "deep"),
        ("🤖 Robot", "robot"),
        ("📻 Radio", "radio"),
        ("🌌 Echo", "echo"),
        ("🎵 Bass", "bass")
    ]

    for name, value in filters:
        keyboard.insert(InlineKeyboardButton(name, callback_data=f"filter_{value}"))

    await message.reply(
        "🎛️ <b>Select Voice Filter:</b>\n\n"
        "• <b>Deep</b>: Instagram trending voice\n"
        "• <b>Robot</b>: Robotic effect\n"
        "• <b>Radio</b>: AM radio effect\n"
        "• <b>Echo</b>: Echo/Delay effect\n"
        "• <b>Bass</b>: Bass boosted",
        reply_markup=keyboard
    )


@dp.message_handler(Command("status"), chat_type=types.ChatType.PRIVATE)
async def cmd_status(message: types.Message):
    """Check bot status"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await message.reply("Please use /start first!")
        return

    status_text = f"""
📊 <b>Bot Status</b>

<b>User:</b> @{message.from_user.username or 'N/A'}
<b>User ID:</b> <code>{user_id}</code>

<b>Group:</b> {user.get('group_title', 'Not set')}
<b>Filter:</b> {user.get('voice_filter', 'deep').title()}
<b>Status:</b> {'🟢 Active' if user.get('is_active') else '🔴 Inactive'}
"""

    await message.reply(status_text)


@dp.message_handler(Command("stats"), chat_type=types.ChatType.PRIVATE)
async def cmd_stats(message: types.Message):
    """User statistics"""
    user_id = message.from_user.id

    # Check owner
    if user_id != Config.OWNER_ID:
        await message.reply("❌ Owner only command!")
        return

    stats = await db.get_user_stats(user_id)
    total_users = await db.db.users.count_documents({})
    active_users = len(await db.get_active_users())

    stats_text = f"""
📈 <b>Bot Statistics</b>

<b>Total Users:</b> {total_users}
<b>Active Users:</b> {active_users}
<b>Your Voices:</b> {stats.get('total_voices', 0)}

<b>Filter Usage:</b>
"""

    for filter_name, count in stats.get('filter_stats', {}).items():
        stats_text += f"• {filter_name.title()}: {count}\n"

    await message.reply(stats_text)


@dp.message_handler(Command("debug"), chat_type=types.ChatType.PRIVATE)
async def cmd_debug(message: types.Message):
    """Debug UserBot and VC status"""
    user_id = message.from_user.id
    
    debug_info = []
    debug_info.append(f"<b>👤 Your ID:</b> <code>{user_id}</code>")
    
    # 1. Check if UserBot client exists
    client = userbot_manager.clients.get(user_id)
    if client:
        debug_info.append("✅ <b>UserBot Client:</b> Connected")
        try:
            me = await client.get_me()
            debug_info.append(f"   🤖 Logged in as: @{me.username} (ID: {me.id})")
        except:
            debug_info.append("   ⚠️ Could not fetch user info")
    else:
        debug_info.append("❌ <b>UserBot Client:</b> Not connected (did /on work?)")
    
    # 2. Check active voice chat
    active_vc = userbot_manager.active_chats.get(user_id)
    if active_vc:
        debug_info.append(f"✅ <b>Voice Chat:</b> Joined (Chat ID: <code>{active_vc}</code>)")
    else:
        debug_info.append("❌ <b>Voice Chat:</b> Not joined")
    
    # 3. Get user's configured chat ID from database
    user_data = await db.get_user(user_id)
    config_chat_id = user_data.get("chat_id") if user_data else None
    debug_info.append(f"📁 <b>Configured Group ID in DB:</b> <code>{config_chat_id}</code>")
    
    # Send with HTML parsing
    await message.reply("\n".join(debug_info), parse_mode="HTML")


@dp.message_handler(Command("configcheck"), chat_type=types.ChatType.PRIVATE)
async def cmd_configcheck(message: types.Message):
    """Check config status"""
    from config import Config
    
    # Get config status
    status = Config.get_env_status()
    
    # Check session validity
    valid, msg = Config.check_session_validity()
    session_status = f"Session: {'✅ ' + msg if valid else '❌ ' + msg}"
    
    await message.reply(f"{status}\n\n{session_status}", parse_mode="HTML")


@dp.message_handler(Command("envtest"), chat_type=types.ChatType.PRIVATE)
async def cmd_envtest(message: types.Message):
    """Test environment variables"""
    from config import Config
    
    test_results = []
    test_results.append("<b>🧪 Environment Test Results</b>")
    test_results.append("="*40)
    
    # Test 1: Basic validation
    try:
        Config.validate()
        test_results.append("✅ Basic validation: PASSED")
    except ValueError as e:
        test_results.append(f"❌ Basic validation: FAILED - {str(e)}")
    
    # Test 2: Session string check
    valid, msg = Config.check_session_validity()
    test_results.append(f"{'✅' if valid else '❌'} Session check: {msg}")
    
    # Test 3: Required variables
    required_vars = [
        ("BOT_TOKEN", Config.BOT_TOKEN),
        ("API_ID", Config.API_ID),
        ("API_HASH", Config.API_HASH),
        ("SESSION_STRING", Config.SESSION_STRING),
        ("MONGO_URI", Config.MONGO_URI),
        ("OWNER_ID", Config.OWNER_ID)
    ]
    
    test_results.append("\n<b>Required Variables:</b>")
    all_good = True
    for name, value in required_vars:
        if value:
            test_results.append(f"  ✅ {name}")
        else:
            test_results.append(f"  ❌ {name} - MISSING")
            all_good = False
    
    test_results.append(f"\n{'🎉 All tests passed!' if all_good else '⚠️ Some tests failed!'}")
    
    await message.reply("\n".join(test_results), parse_mode="HTML")


@dp.message_handler(Command("testuserbot"), chat_type=types.ChatType.PRIVATE)
async def cmd_testuserbot(message: types.Message):
    """Directly test UserBot connection"""
    from config import Config
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    
    debug_info = []
    debug_info.append("<b>🧪 UserBot Direct Test</b>")
    
    # Step 1: Check config
    debug_info.append("\n<b>📋 Config Check:</b>")
    debug_info.append(f"API_ID: {Config.API_ID}")
    debug_info.append(f"API_HASH: {'✅ Set' if Config.API_HASH else '❌ Missing'}")
    debug_info.append(f"SESSION_STRING: {'✅ Set' if Config.SESSION_STRING else '❌ Missing'}")
    if Config.SESSION_STRING:
        debug_info.append(f"SESSION_STRING length: {len(Config.SESSION_STRING)} chars")
    
    # Step 2: Try direct connection
    debug_info.append("\n<b>🔗 Direct Connection Test:</b>")
    
    if not Config.SESSION_STRING:
        debug_info.append("❌ SESSION_STRING is empty!")
        await message.reply("\n".join(debug_info), parse_mode="HTML")
        return
    
    client = None
    try:
        debug_info.append("1. Creating Telethon client...")
        
        # Direct test
        client = TelegramClient(
            StringSession(Config.SESSION_STRING),
            Config.API_ID,
            Config.API_HASH
        )
        
        debug_info.append("2. Connecting to Telegram...")
        await client.connect()
        
        debug_info.append("3. Checking authorization...")
        if not await client.is_user_authorized():
            debug_info.append("❌ NOT AUTHORIZED - Session invalid/expired!")
            await client.disconnect()
        else:
            me = await client.get_me()
            debug_info.append(f"✅ AUTHORIZED as @{me.username} (ID: {me.id})")
            
            # Try to send a test message
            try:
                await client.send_message("me", "✅ UserBot test from Railway - Bot is working!")
                debug_info.append("✅ Test message sent to Saved Messages")
            except Exception as e:
                debug_info.append(f"⚠️ Message test failed: {str(e)}")
            
            await client.disconnect()
            debug_info.append("✅ Disconnected successfully")
            debug_info.append("\n🎉 <b>UserBot is WORKING correctly!</b>")
            
    except Exception as e:
        debug_info.append(f"❌ Connection failed: {type(e).__name__}: {str(e)}")
        
        # Try to get more specific error
        error_str = str(e).lower()
        if "invalid" in error_str or "expired" in error_str:
            debug_info.append("\n⚠️ <b>SESSION STRING INVALID or EXPIRED</b>")
            debug_info.append("Generate new session string using Termux")
        elif "timeout" in error_str:
            debug_info.append("\n⚠️ <b>NETWORK TIMEOUT</b>")
            debug_info.append("Check Railway network connectivity")
        elif "password" in error_str:
            debug_info.append("\n⚠️ <b>2FA PASSWORD REQUIRED</b>")
            debug_info.append("Your account has 2FA enabled")
        
        if client:
            try:
                await client.disconnect()
            except:
                pass
    
    # Send final report
    await message.reply("\n".join(debug_info), parse_mode="HTML")


@dp.message_handler(Command("help"), chat_type=types.ChatType.PRIVATE)
async def cmd_help(message: types.Message):
    """Show help menu"""
    help_text = """
🎤 <b>InstaVoice Bot - Help Menu</b>

<b>📱 Basic Commands:</b>
/start - Start the bot
/on - Activate bot & join VC
/off - Deactivate bot
/stop - Leave voice chat
/setgc - Set group chat
/filter - Change voice filter
/status - Check bot status

<b>🔧 Debug Commands:</b>
/debug - Check UserBot status
/configcheck - Check configuration
/envtest - Test environment variables
/testuserbot - Test UserBot directly

<b>👑 Owner Commands:</b>
/stats - View bot statistics

<b>⚡ Quick Guide:</b>
1. Add bot to group (make admin)
2. Use /setgc with group link
3. Use /on to activate
4. Send voice notes to bot
5. Voice will play in group VC

<b>❓ Need Help?</b>
If bot doesn't work:
1. Use /testuserbot to check UserBot
2. Use /debug to see current status
3. Check Railway logs for errors
"""

    await message.reply(help_text, parse_mode="HTML")
