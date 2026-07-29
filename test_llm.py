import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from marketing_agent.llm_client import llm_chat, API_KEY, NINE_ROUTER_URL
print("NINE_ROUTER_URL:", NINE_ROUTER_URL)
print("API_KEY loaded:", bool(API_KEY and API_KEY != 'sk-default'))
print("API_KEY prefix:", API_KEY[:10] if API_KEY else "EMPTY")
# Test a quick chat
text = llm_chat("Say hello in one word.")
print("Response:", text[:100])