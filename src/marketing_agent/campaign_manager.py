import os
from datetime import datetime
from .db import get_conn, gen_id, init_db

class CampaignManager:
    def __init__(self):
        init_db()

    def plan_campaign(self, name, objective, target_audience, budget, platform_name=None, platform_campaign_id=None):
        conn = get_conn()
        cid = gen_id("camp")
        conn.execute("INSERT INTO campaigns (id, name, objective, target_audience, budget, status, created_at, platform_name, platform_campaign_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (cid, name, objective, target_audience, budget, 'planned', datetime.now().isoformat(), platform_name, platform_campaign_id))
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

    def update_campaign_platform_info(self, campaign_id, platform_name, platform_campaign_id):
        conn = get_conn()
        conn.execute("UPDATE campaigns SET platform_name = ?, platform_campaign_id = ? WHERE id = ?",
                     (platform_name, platform_campaign_id, campaign_id))
        conn.commit()
        conn.close()
        return f"Platform info updated for campaign {campaign_id}"

    def execute_campaign(self, campaign_id):
        campaign = self.get_campaign_by_id(campaign_id)
        if not campaign:
            return "Campaign not found."

        if campaign['status'] == 'planned':
            conn = get_conn()
            conn.execute("UPDATE campaigns SET status = 'executing' WHERE id = ?", (campaign_id,))
            conn.commit()
            conn.close()
            # Placeholder for actual execution logic (e.g., calling Google Ads API)
            # This is where we'll integrate with platform clients later
            return f"Campaign {campaign_id} started execution."
        elif campaign['status'] == 'executing':
            return f"Campaign {campaign_id} is already executing."
        else:
            return f"Campaign {campaign_id} cannot be executed in current status ({campaign['status']})."
