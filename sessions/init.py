"""
Session management
"""
import os
import json

SESSIONS_DIR = "sessions"

def ensure_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, exist_ok=True)

def save_session(user_id: int, data: dict):
    ensure_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{user_id}.json")
    with open(filepath, "w") as f:
        json.dump(data, f)

def load_session(user_id: int):
    filepath = os.path.join(SESSIONS_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None
