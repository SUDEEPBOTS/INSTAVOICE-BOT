"""
Temp file management
"""
import os
import time

TEMP_DIR = "temp"

def ensure_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_old(hours: int = 24):
    ensure_dir()
    cutoff = time.time() - (hours * 3600)
    
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
        except:
            pass
