import json
import os
from datetime import datetime
from .governance import audit_tracer, budget_manager
from .campaign_manager import STORAGE_FILE as CAMPAIGN_STORAGE_FILE

class Dashboard:
    def get_overview(self):
        overview = {
            "last_updated": datetime.now().isoformat(),
            "campaigns": self._get_campaign_summary(),
            "audit_log_count": len(audit_tracer.trace_log),
            "budget_remaining": budget_manager.get_remaining_budget()
        }
        return overview

    def _get_campaign_summary(self):
        campaign_summary = {
            "total_campaigns": 0,
            "planned": 0,
            "executing": 0,
            "completed": 0,
            "total_budget_allocated": 0
        }
        if os.path.exists(CAMPAIGN_STORAGE_FILE):
            try:
                with open(CAMPAIGN_STORAGE_FILE, 'r') as f:
                    campaigns = json.load(f)
                    campaign_summary["total_campaigns"] = len(campaigns)
                    for cid, campaign_data in campaigns.items():
                        campaign_summary["total_budget_allocated"] += campaign_data.get('budget', 0)
                        status = campaign_data.get('status', 'unknown')
                        if status == 'planned':
                            campaign_summary["planned"] += 1
                        elif status == 'executing':
                            campaign_summary["executing"] += 1
                        elif status == 'completed':
                            campaign_summary["completed"] += 1
            except Exception as e:
                print(f"Error loading campaign data for dashboard: {e}")
        return campaign_summary

dashboard = Dashboard()
