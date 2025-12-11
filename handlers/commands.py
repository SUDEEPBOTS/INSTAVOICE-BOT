# handlers/commands.py
"""
Command handlers (aiogram v3, Router-based)
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import Config
from database import db
from utils.userbot_manager import userbot_manager
from handlers.states import UserStates

router = Router()


def _is_private(chat: types.Chat) -> bool:
    try:
        return chat.type == types.ChatType.PRIVATE
    except Exception:
        return False


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command (private chats only)"""
    if not _is_private(message.chat):
        return

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or "User"

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

<b>⚡ Quick Setup:</b>
1. Add me to group (make admin)
2. /setgc + group link
3. /on to activate
4. Send voice notes!

Made with ❤️ by @{username or 'InstaVoice'}
"""

    await message.reply(welcome)


@router.message(Command("on"))
async def cmd_on(message: types.Message):
    """Activate bot"""
    if not _is_private(message.chat):
        return

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


@router.message(Command("off"))
async def cmd_off(message: types.Message):
    """Deactivate bot"""
    if not _is_private(message.chat):
        return

    user_id = message.from_user.id

    await userbot_manager.leave_voice_chat(user_id)
    await db.set_active(user_id, False)
    await userbot_manager.stop_client(user_id)

    await message.reply("✅ Bot deactivated!")


@router.message(Command("stop"))
async def cmd_stop(message: types.Message):
    """Leave voice chat"""
    if not _is_private(message.chat):
        return

    user_id = message.from_user.id

    await userbot_manager.leave_voice_chat(user_id)
    await db.set_active(user_id, False)

    await message.reply("✅ Left voice chat!")


@router.message(Command("setgc"))
async def cmd_setgc(message: types.Message, state: FSMContext):
    """Set group chat - ask for link"""
    if not _is_private(message.chat):
        return

    await state.set_state(UserStates.waiting_for_gc_link)
    await message.reply("Please send your group link (e.g., https://t.me/groupname or @groupname):")


@router.message()  # will process messages while in state
async def process_gc_link(message: types.Message, state: FSMContext):
    """Process group link when user is in waiting_for_gc_link state"""
    current_state = await state.get_state()
    if current_state != UserStates.waiting_for_gc_link.state:
        return  # not our state, ignore

    try:
        link = (message.text or "").strip()
        user_id = message.from_user.id

        # Extract username
        if "t.me/" in link:
            username = link.split("t.me/")[-1].replace("@", "").strip()
        elif link.startswith("@"):
            username = link[1:].strip()
        else:
            await message.reply("Invalid format! Use: https://t.me/username or @username")
            await state.clear()
            return

        # Get chat info (import bot here to avoid circular import)
        from bot import bot
        chat = await bot.get_chat(f"@{username}")

        # Save to DB
        await db.set_group(
            user_id=user_id,
            chat_id=chat.id,
            title=getattr(chat, "title", username),
            username=username
        )

        await message.reply(
            f"✅ Group set successfully!\n\n"
            f"<b>Group:</b> {getattr(chat, 'title', username)}\n"
            f"<b>ID:</b> <code>{chat.id}</code>\n\n"
            f"Now use /on to activate!"
        )

    except Exception as e:
        await message.reply(
            f"Error: {str(e)}\n\nMake sure:\n"
            f"1. Bot is added to group\n2. Bot is admin"
        )
    finally:
        await state.clear()


@router.message(Command("filter"))
async def cmd_filter(message: types.Message):
    """Change voice filter"""
    if not _is_private(message.chat):
        return

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


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    """Check bot status"""
    if not _is_private(message.chat):
        return

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


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """User statistics (owner only)"""
    if not _is_private(message.chat):
        return

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


# Export router as `dp` so bot.py can do: from handlers.commands import dp as commands_dp
dp = router
