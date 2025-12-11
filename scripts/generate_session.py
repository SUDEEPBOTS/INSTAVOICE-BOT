#!/usr/bin/env python3
"""
Generate Telethon session string for Termux
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    print("\n" + "="*50)
    print("🔧 TELEGRAM SESSION GENERATOR FOR TERMUX")
    print("="*50)
    
    # Get credentials
    api_id = input("\nEnter API ID (from my.telegram.org): ").strip()
    api_hash = input("Enter API HASH: ").strip()
    phone = input("Enter phone number (with country code): ").strip()
    
    try:
        # Create client
        client = TelegramClient(
            StringSession(),
            int(api_id),
            api_hash
        )
        
        await client.connect()
        
        # Send code
        print("\n📲 Sending code to Telegram...")
        sent = await client.send_code_request(phone)
        phone_code_hash = sent.phone_code_hash
        
        # Get code
        code = input("Enter the code you received: ").strip()
        
        # Sign in
        try:
            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_code_hash
            )
        except Exception as e:
            if "two-steps" in str(e).lower():
                password = input("Enter 2FA password: ").strip()
                await client.sign_in(password=password)
            else:
                raise e
        
        # Get session string
        session_string = client.session.save()
        
        # Get user info
        me = await client.get_me()
        
        print("\n" + "="*50)
        print("✅ SESSION GENERATED SUCCESSFULLY!")
        print("="*50)
        print(f"\n👤 User: @{me.username}")
        print(f"📱 Phone: {me.phone}")
        print(f"🆔 ID: {me.id}")
        
        print("\n📝 SESSION STRING (Copy this to Railway .env):")
        print("="*60)
        print(session_string)
        print("="*60)
        
        print("\n💡 Paste this in Railway .env as:")
        print(f"SESSION_STRING={session_string}")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())
