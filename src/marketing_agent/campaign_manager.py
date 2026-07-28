import random
import json
import os

STORAGE_FILE = 'campaign_data.json'

class CampaignManager:
    def __init__(self):
        self.campaigns = {}
        self.load()

    def save(self):
        with open(STORAGE_FILE, 'w') as f:
            json.dump(self.campaigns, f, indent=2)

    def load(self):
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, 'r') as f:
                    self.campaigns = json.load(f)
            except:
                self.campaigns = {}

    def plan_campaign(self, name, objective, target_audience, budget):
        campaign_id = f"cmp_{random.randint(1000, 9999)}"
        self.campaigns[campaign_id] = {
            'name': name,
            'objective': objective,
            'target_audience': target_audience,
            'budget': budget,
            'status': 'planned'
        }
        self.save()
        return campaign_id

    def execute_campaign(self, name):
        for cid, c in self.campaigns.items():
            if c['name'] == name:
                if c['status'] == 'planned':
                    c['status'] = 'executing'
                    self.save()
                    return f"Campaign '{name}' ({cid}) execution started."
                else:
                    return f"Campaign '{name}' ({cid}) is already in '{c['status']}' state."
        return f"Campaign '{name}' not found."

campaign_manager = CampaignManager()
