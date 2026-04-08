import sqlite3
import bcrypt
import json
from datetime import datetime

DB = "retinal.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            diagnosis TEXT,
            confidence REAL,
            probabilities TEXT,
            image_name TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def register_user(name, email, password):
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password, created_at) VALUES (?,?,?,?)",
                  (name, email, hashed, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already registered."

def login_user(email, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, password FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[2].encode()):
        return True, {"id": row[0], "name": row[1], "email": email}
    return False, "Invalid email or password."

def save_prediction(user_id, diagnosis, confidence, probabilities, image_name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""INSERT INTO predictions (user_id, diagnosis, confidence, probabilities, image_name, created_at)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, diagnosis, confidence, json.dumps(probabilities), image_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows