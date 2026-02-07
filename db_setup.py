import sqlite3
import os
from passlib.hash import bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

print("Creating DB at:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    phone TEXT,
    role TEXT,
    family_doctor TEXT
)
""")

users = [
    ("Axiaevangelin", bcrypt.hash("Axia@1910"),
     "axia@mail.com","9000000001","Patient","Dr. Kumar"),

    ("Vinodha", bcrypt.hash("Vino@123"),
     "vino@mail.com","9000000002","Patient","Dr. Anjali"),

    ("Test", bcrypt.hash("Test@123"),
     "test@mail.com","9000000003","Patient","Dr. Rao"),
    
    ("Aakash", bcrypt.hash("Aak@123"),
     "aakash@mail.com","9000000004","Patient","Dr. Singh")
    
]

for u in users:
    try:
        cur.execute("""
        INSERT INTO users
        (username,password,email,phone,role,family_doctor)
        VALUES (?,?,?,?,?,?)
        """, u)
        print("Inserted:", u[0])
    except Exception as e:
        print("Skip:", u[0])

conn.commit()
conn.close()

print("Database ready ✅")
