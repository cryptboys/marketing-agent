import json
from datetime import datetime
from .db import get_conn, init_db


class BudgetManager:
    def __init__(self):
        init_db()

    def _load(self):
        conn = get_conn()
        rows = {r['key']: r['value'] for r in conn.execute("SELECT key, value FROM config WHERE key IN ('budget_total', 'budget_spent')").fetchall()}
        conn.close()
        return float(rows.get('budget_total', 10000)), float(rows.get('budget_spent', 0))

    def consume_budget(self, amount):
        total, spent = self._load()
        if total - spent >= amount:
            conn = get_conn()
            conn.execute("UPDATE config SET value = ? WHERE key = 'budget_spent'", (str(spent + amount),))
            conn.commit()
            conn.close()
            return True
        return False

    def get_remaining_budget(self):
        total, spent = self._load()
        return total - spent


budget_manager = BudgetManager()


class EgressValidator:
    def __init__(self, allowed_domains=None):
        self.allowed_domains = allowed_domains or []

    def is_allowed(self, url):
        for domain in self.allowed_domains:
            if domain in url:
                return True
        return False


egress_validator = EgressValidator()


class AuditTracer:
    def __init__(self):
        init_db()

    def add_trace(self, action, details):
        conn = get_conn()
        conn.execute(
            "INSERT INTO audit_logs (action, details, timestamp) VALUES (?, ?, ?)",
            (action, json.dumps(details, default=str), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    @property
    def trace_log(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 200").fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d['details'] = json.loads(d['details']) if d['details'] else {}
            except:
                d['details'] = {}
            result.append(d)
        return result


audit_tracer = AuditTracer()