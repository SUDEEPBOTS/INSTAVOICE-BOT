"""
Helper functions
"""
import os
import time
from datetime import datetime, timedelta

def cleanup_temp_files(directory: str = "temp_voices", hours: int = 24):
    """Cleanup old temporary files"""
    if not os.path.exists(directory):
        return 0
        
    deleted = 0
    cutoff = time.time() - (hours * 3600)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        try:
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                deleted += 1
        except:
            pass
            
    return deleted
    
def format_time(seconds: int) -> str:
    """Format seconds to readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m = seconds // 60
        s = seconds % 60
        return f"{m}m {s}s"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m"
        
def get_file_size(filepath: str) -> str:
    """Get human readable file size"""
    size = os.path.getsize(filepath)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
        
    return f"{size:.1f} TB"
    
def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    from config import Config
    return user_id == Config.OWNER_ID
