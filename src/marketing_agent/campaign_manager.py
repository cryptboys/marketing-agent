import os
from .db import get_conn, gen_id, init_db

class CampaignManager:
    def __init__(self):
        init_db()

    def plan_campaign(self, name, objective, target_audience, budget):
        conn = get_conn()
        cid = gen_id("camp")
        conn.execute("INSERT INTO campaigns VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (cid, name, objective, target_audience, budget, 'planned', os.datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return cid

    def get_campaign_by_id(self, campaign_id):
        conn = get_conn()
        row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_campaigns(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM campaigns").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def execute_campaign(self, campaign_id):
        # Implementation of campaign execution
        conn = get_conn()
        conn.execute("UPDATE campaigns SET status = 'executing' WHERE id = ?", (campaign_id,))
        conn.commit()
        conn.close()
        return f"Campaign {campaign_id} started execution."
