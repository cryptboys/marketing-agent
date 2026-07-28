import sqlite3
import os
import random
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'marketing.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            objective TEXT,
            target_audience TEXT,
            budget REAL DEFAULT 0,
            status TEXT DEFAULT 'planned',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            source TEXT,
            score INTEGER DEFAULT 50,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    # Insert default budget if not exists
    conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('budget_total', '10000')")
    conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('budget_spent', '0')")
    conn.commit()
    conn.close()

def gen_id(prefix):
    return f"{prefix}_{random.randint(1000, 9999)}"