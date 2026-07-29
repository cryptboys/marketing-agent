import requests
import json
import os

env_path = r'C:\Users\Advan\.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

NINE_ROUTER_URL = os.getenv('NINE_ROUTER_URL', 'http://localhost:20128/v1')
API_KEY = os.environ.get('NINE_ROUTER_API_KEY', 'sk-default')
DEFAULT_MODEL = 'easy'

def llm_chat(prompt, system_prompt="You are a helpful marketing assistant.", model=DEFAULT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(f"{NINE_ROUTER_URL}/chat/completions", headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        raw = r.text
        # Clean streaming artifacts from response
        raw = raw.replace('data: [DONE]', '').strip()
        # Try to find the first valid JSON object/array
        # If raw has extra data, extract only the JSON part
        lines = raw.split('\n')
        json_part = None
        for line in lines:
            line = line.strip()
            if line.startswith('{') or line.startswith('['):
                try:
                    json_part = json.loads(line)
                    break
                except:
                    continue
        if json_part is None:
            # Fallback: try parsing the whole thing
            json_part = json.loads(raw) if raw else {}
        data = json_part
        text = data.get('choices', [{}])[0].get('message', {}).get('content', str(data))
        text = text.replace('data: [DONE]', '').strip()
        if text.startswith('[') or text.startswith('{'):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    text = '\n'.join(str(item) for item in parsed)
                elif isinstance(parsed, dict):
                    text = str(parsed)
            except:
                pass
        return text
    except Exception as e:
        raise Exception(f"API call failed: {e}")
