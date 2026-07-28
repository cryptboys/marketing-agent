import random
import json
from .llm_client import llm_chat

class DataAnalyzer:
    def analyze_keywords(self, keywords):
        kw_list = ", ".join(keywords)
        prompt = f"""Analyze these marketing keywords: {kw_list}.
For each keyword, return a JSON array with objects having: keyword, search_volume (1-10000), competition (low/medium/high).
Return ONLY the JSON array, no other text."""
        
        result = llm_chat(prompt, model="easy")
        if result:
            try:
                data = json.loads(result)
                return {item["keyword"]: {"search_volume": item["search_volume"], "competition": item["competition"]} for item in data}
            except:
                pass
        # fallback mock
        return {kw: {"search_volume": random.randint(100, 10000), "competition": random.choice(["low", "medium", "high"])} for kw in keywords}

data_analyzer = DataAnalyzer()
