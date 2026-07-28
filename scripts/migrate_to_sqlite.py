#!/usr/bin/env python3
""""
Import existing JSON data into SQLite.
Run once before running for first time with new schema.
"""
import json
import os
import sys
# Add the parent directory of 'src' to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.marketing_agent.db import get_conn, init_db

def load_json(path):
    # Adjust path for JSON file
    adjusted_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
    if os.path.exists(adjusted_path):
        with open(adjusted_path, 'r') as f:
            return json.load(f)
    return {}

def migrate_campaigns():
    data = load_json('campaign_data.json')
    conn = get_conn()
    for cid, info in data.items():
        conn.execute("""
            INSERT OR IGNORE INTO campaigns (id, name, objective, target_audience, budget, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cid, info.get('name'), info.get('objective'), info.get('target_audience'), info.get('budget'), info.get('status')))
    conn.commit()
    conn.close()
    print(f"Imported {len(data)} campaigns")

def migrate_leads():
    # No existing leads JSON; placeholder
    pass

def migrate_audit():
    # Load all tool/trace logs from Hermes audit traces if any
    # For now, no existing audit JSON; placeholder
    pass

def migrate_config():
    # Ensure budget configs exist
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('budget_total', '10000')")
    conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('budget_spent', '0')")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Migrating JSON data to SQLite...")
    init_db()
    migrate_campaigns()
    migrate_leads()
    migrate_audit()
    migrate_config()
    print("Migration complete.")
