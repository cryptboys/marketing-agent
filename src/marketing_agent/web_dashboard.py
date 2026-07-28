from flask import Flask, jsonify
from marketing_agent.dashboard import dashboard
from marketing_agent.campaign_manager import campaign_manager

app = Flask(__name__)

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify(dashboard.get_overview())

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    return jsonify(campaign_manager.campaigns)

if __name__ == '__main__':
    print("Dashboard server running at http://localhost:5000")
    app.run(port=5000)
