#!/usr/bin/env python3
"""
Script to migrate the campaigns table by adding new columns for platform integration.
This script will create a new table with the updated schema and copy data over.
"""
import sqlite3
import os
import sys
import random
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def gen_id(prefix):
    return f"{prefix}-{random.randint(1000, 9999)}{datetime.now().strftime('%f')}"

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marketing.db')
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns exist
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'platform_name' not in columns:
            # Table exists but needs columns added
            cursor.execute("ALTER TABLE campaigns ADD COLUMN platform_name TEXT DEFAULT NULL")
            print("Added column platform_name")
        
        if 'platform_campaign_id' not in columns:
            cursor.execute("ALTER TABLE campaigns ADD COLUMN platform_campaign_id TEXT DEFAULT NULL")
            print("Added column platform_campaign_id")
        
        conn.commit()
        print("Migration complete. Updating init_db schema...")

    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()
