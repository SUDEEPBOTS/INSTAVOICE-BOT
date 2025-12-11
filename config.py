import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    
    # Database
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "instavoicebot")
    
    # Owner
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    
    # Voice Settings
    VOICE_PITCH_SHIFT = int(os.getenv("VOICE_PITCH_SHIFT", -4))
    VOICE_BASS_BOOST = int(os.getenv("VOICE_BASS_BOOST", 8))
    VOICE_REVERB = float(os.getenv("VOICE_REVERB", 0.15))
    VOICE_SPEED = float(os.getenv("VOICE_SPEED", 0.92))
    
    # Bot Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_VOICE_SIZE = int(os.getenv("MAX_VOICE_SIZE", 20)) * 1024 * 1024
    CLEANUP_HOURS = int(os.getenv("CLEANUP_HOURS", 24))
    
    @classmethod
    def debug_info(cls):
        """Debug info for checking config"""
        return {
            "BOT_TOKEN": "✅ Set" if cls.BOT_TOKEN else "❌ Missing",
            "API_ID": cls.API_ID,
            "API_HASH": "✅ Set" if cls.API_HASH else "❌ Missing",
            "SESSION_STRING": f"✅ Length: {len(cls.SESSION_STRING)} chars" if cls.SESSION_STRING else "❌ Missing",
            "OWNER_ID": cls.OWNER_ID,
            "MONGO_URI": "✅ Set" if cls.MONGO_URI else "❌ Missing",
            "DB_NAME": cls.DB_NAME
        }
    
    @classmethod
    def get_config_summary(cls):
        """Get safe config summary (hides sensitive data)"""
        summary = []
        summary.append("📋 <b>Config Summary</b>")
        summary.append(f"API_ID: {cls.API_ID}")
        summary.append(f"API_HASH: {'✅' if cls.API_HASH else '❌'}")
        summary.append(f"SESSION_STRING: {'✅' if cls.SESSION_STRING else '❌'}")
        if cls.SESSION_STRING:
            summary.append(f"  Length: {len(cls.SESSION_STRING)} chars")
            summary.append(f"  Starts with: {cls.SESSION_STRING[:10]}...")
        summary.append(f"OWNER_ID: {cls.OWNER_ID}")
        summary.append(f"DB_NAME: {cls.DB_NAME}")
        summary.append(f"MONGO_URI: {'✅ Set' if cls.MONGO_URI else '❌ Missing'}")
        return "\n".join(summary)
    
    @classmethod
    def validate(cls):
        """Validate required environment variables"""
        required = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "SESSION_STRING": cls.SESSION_STRING,
            "MONGO_URI": cls.MONGO_URI,
            "OWNER_ID": cls.OWNER_ID
        }
        
        missing = [k for k, v in required.items() if not v]
        if missing:
            error_msg = f"Missing environment variables: {', '.join(missing)}"
            print(f"❌ CONFIG ERROR: {error_msg}")
            raise ValueError(error_msg)
        
        print("✅ Config validated successfully")
        
        # Print debug info
        debug_info = cls.debug_info()
        print("\n📋 Config Debug Info:")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        
        return True
    
    @classmethod
    def check_session_validity(cls):
        """Quick check if session string looks valid"""
        if not cls.SESSION_STRING:
            return False, "Session string is empty"
        
        # Basic format checks
        if len(cls.SESSION_STRING) < 100:
            return False, f"Session too short ({len(cls.SESSION_STRING)} chars)"
        
        if not cls.SESSION_STRING[0].isdigit():
            return False, f"Session doesn't start with digit (starts with: {cls.SESSION_STRING[0]})"
        
        # Common patterns in Telethon session strings
        common_patterns = ["1Ap", "1Aq", "1Ag", "1B"]
        if not any(cls.SESSION_STRING.startswith(pattern) for pattern in common_patterns):
            return False, "Session doesn't match common Telethon patterns"
        
        return True, f"Session looks valid ({len(cls.SESSION_STRING)} chars)"
    
    @classmethod
    def get_env_status(cls):
        """Get status of all environment variables"""
        env_vars = [
            ("BOT_TOKEN", cls.BOT_TOKEN, True),
            ("API_ID", cls.API_ID, True),
            ("API_HASH", cls.API_HASH, True),
            ("SESSION_STRING", cls.SESSION_STRING, True),
            ("MONGO_URI", cls.MONGO_URI, True),
            ("OWNER_ID", cls.OWNER_ID, True),
            ("DB_NAME", cls.DB_NAME, False),
            ("VOICE_PITCH_SHIFT", cls.VOICE_PITCH_SHIFT, False),
            ("VOICE_BASS_BOOST", cls.VOICE_BASS_BOOST, False),
            ("VOICE_REVERB", cls.VOICE_REVERB, False),
            ("VOICE_SPEED", cls.VOICE_SPEED, False),
            ("LOG_LEVEL", cls.LOG_LEVEL, False),
            ("MAX_VOICE_SIZE", cls.MAX_VOICE_SIZE // (1024*1024), False),
            ("CLEANUP_HOURS", cls.CLEANUP_HOURS, False)
        ]
        
        status = []
        status.append("<b>🔧 Environment Variables Status</b>")
        status.append("="*40)
        
        for name, value, required in env_vars:
            if required:
                status.append(f"{name}: {'✅ SET' if value else '❌ MISSING (REQUIRED)'}")
            else:
                status.append(f"{name}: {value if value else '⚠️ Not set (using default)'}")
        
        return "\n".join(status)
