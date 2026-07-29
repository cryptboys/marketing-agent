import sqlite3
import os
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'marketing.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            objective TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            budget REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            platform_name TEXT DEFAULT NULL,
            platform_campaign_id TEXT DEFAULT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrations (
            id TEXT PRIMARY KEY,
            platform TEXT UNIQUE NOT NULL,
            client_id TEXT NOT NULL,
            client_secret TEXT NOT NULL,
            developer_token TEXT,
            refresh_token TEXT,
            customer_id TEXT,
            expires_at TEXT,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def gen_id(prefix):
    return f"{prefix}-{random.randint(1000, 9999)}{datetime.now().strftime('%f')}"

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        conn = get_conn()
        is_likely_id = '-' in user_id and any(char.isdigit() for char in user_id)
        
        if is_likely_id:
            row = conn.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        else:
            row = conn.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (user_id,)).fetchone()
            
        conn.close()
        if row:
            return User(row['id'], row['username'], row['password_hash'])
        return None

    @staticmethod
    def create(username, password):
        conn = get_conn()
        hashed_password = generate_password_hash(password)
        user_id = gen_id("user")
        try:
            conn.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                         (user_id, username, hashed_password))
            conn.commit()
            return User(user_id, username, hashed_password)
        except sqlite3.IntegrityError:
            conn.close()
            return None 
        finally:
            conn.close()