import os
from .db import get_conn, gen_id, init_db

class CampaignManager:
    def __init__(self):
        init_db()

    def plan_campaign(self, name, objective, target_audience, budget):
        cid = gen_id("cmp")
        conn = get_conn()
        conn.execute(
            "INSERT INTO campaigns (id, name, objective, target_audience, budget, status) VALUES (?, ?, ?, ?, ?, 'planned')",
            (cid, name, objective, target_audience, budget)
        )
        conn.commit()
        conn.close()
        return cid

    def execute_campaign(self, name):
        conn = get_conn()
        # Get campaign by name first to find its ID
        row_by_name = conn.execute("SELECT id, status FROM campaigns WHERE name = ?", (name,)).fetchone()
        if not row_by_name:
            conn.close()
            return f"Campaign '{name}' not found."

        campaign_id, current_status = row_by_name['id'], row_by_name['status']

        if current_status == 'planned':
            conn.execute("UPDATE campaigns SET status='executing', updated_at=datetime('now') WHERE id=?", (campaign_id,))
            conn.commit()
            conn.close()
            return f"Campaign '{name}' ({campaign_id}) execution started."
        else:
            conn.close()
            return f"Campaign '{name}' ({campaign_id}) is already in '{current_status}' state."

    @property
    def campaigns(self):
        conn = get_conn()
        rows = conn.execute("SELECT id, name, objective, target_audience, budget, status FROM campaigns ORDER BY created_at DESC").fetchall()
        conn.close()
        # Return as dict for consistency with previous JSON structure
        return {r['id']: dict(r) for r in rows}

campaign_manager = CampaignManager()
