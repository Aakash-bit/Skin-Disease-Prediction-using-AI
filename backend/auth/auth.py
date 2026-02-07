import json
import os
import hashlib
from datetime import datetime

# -----------------------------
# User database file
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
USER_FILE = os.path.join(BASE_DIR, "users.json")

# -----------------------------
# Utilities
# -----------------------------
def load_users():
    if not os.path.exists(USER_FILE) or os.path.getsize(USER_FILE) == 0:
        return []
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# Register User
# -----------------------------
def register_user(username: str, password: str):
    users = load_users()

    if any(u["username"] == username for u in users):
        return {"success": False, "message": "Username already exists"}

    users.append({
        "username": username,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    })

    save_users(users)
    return {"success": True, "message": "User registered successfully"}

# -----------------------------
# Authenticate User
# -----------------------------
def authenticate_user(username: str, password: str):
    users = load_users()
    hashed = hash_password(password)

    for user in users:
        if user["username"] == username and user["password"] == hashed:
            return {"success": True}

    return {"success": False, "message": "Invalid username or password"}
