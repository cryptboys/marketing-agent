# Handles CRM-related tasks
import random

class CRMManager:
    def __init__(self):
        self.leads = {}

    def add_lead(self, name, email, source):
        lead_id = f"lead_{random.randint(1000, 9999)}"
        self.leads[lead_id] = {
            'name': name,
            'email': email,
            'source': source,
            'score': random.randint(0, 100),
            'status': 'new'
        }
        return lead_id

    def get_lead_score(self, lead_id):
        if lead_id in self.leads:
            return self.leads[lead_id]['score']
        return None

crm_manager = CRMManager()
