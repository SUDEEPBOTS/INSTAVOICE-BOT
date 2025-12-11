"""
Log management
"""
import os
from datetime import datetime

LOG_DIR = "logs"

def ensure_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

def get_log_file():
    ensure_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"bot_{date_str}.log")
