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
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        return True
