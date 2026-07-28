import requests
import os
import json

NINE_ROUTER_URL = "http://localhost:20128/v1/chat/completions"
DEFAULT_MODEL = "easy"

def _load_env():
    env_file = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

_load_env()

def llm_chat(prompt, model=DEFAULT_MODEL, system="You are a marketing assistant."):
    api_key = os.environ.get("NINE_ROUTER_API_KEY", "")
    if not api_key:
        return None

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.post(
            NINE_ROUTER_URL,
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            },
            timeout=90
        )
        if resp.status_code != 200:
            return f"[API Error {resp.status_code}]"

        raw = resp.text.strip()
        if raw.endswith("data: [DONE]"):
            raw = raw[:-len("data: [DONE]")].strip()
        if raw.startswith("data: "):
            raw = raw[6:].strip()

        data = json.loads(raw)
        return data["choices"][0]["message"]["content"]

    except json.JSONDecodeError as e:
        return f"[Parse Error: {e}]"
    except Exception as e:
        return f"[Connection Error: {e}]"
