import os
import random
from .db import get_conn, gen_id, init_db

class CRMManager:
    def __init__(self):
        init_db()

    def add_lead(self, name, email, source):
        lid = gen_id("lead")
        score = random.randint(0, 100)
        conn = get_conn()
        conn.execute(
            "INSERT INTO leads (id, name, email, source, score, status) VALUES (?, ?, ?, ?, ?, 'new')",
            (lid, name, email, source, score)
        )
        conn.commit()
        conn.close()
        return lid

    def get_lead_score(self, lead_id):
        conn = get_conn()
        row = conn.execute("SELECT score FROM leads WHERE id = ?", (lead_id,)).fetchone()
        conn.close()
        if row:
            return row['score']
        return None

    @property
    def leads(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
        conn.close()
        return {r['id']: dict(r) for r in rows}

crm_manager = CRMManager()