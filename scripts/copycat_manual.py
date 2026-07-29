"""
Copycat Simplified: Input X post link → Extract → Rewrite → Validate → Post
"""

import re
import json
import os
from datetime import datetime

def extract_post_id_from_url(url):
    """Extract Tweet ID dari X.com URL"""
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else None

def manual_input_post(post_text, source_url):
    """
    Simpan post yang di-copy-paste dari X untuk rewriting.
    User bisa copy text langsung dari X, kita proses di sini.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("vault/research/copycat", today)
    os.makedirs(folder, exist_ok=True)
    
    post_id = extract_post_id_from_url(source_url)
    filename = f"raw_{post_id}.json"
    filepath = os.path.join(folder, filename)
    
    data = {
        "source_url": source_url,
        "raw_text": post_text,
        "timestamp": datetime.now().isoformat(),
        "status": "pending_rewrite"
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def generate_rewrite_prompt(original_post, our_voice_profile):
    """Generate LLM prompt untuk rewrite post dengan voice kita."""
    return f"""You are a brilliant content creator dengan gaya sarkastis, witty, dan street-smart.

ORIGINAL POST (dari creator lain):
"{original_post}"

VOICE PROFILE KAMU:
{our_voice_profile}

TUGAS:
1. Ambil core idea dari post original
2. Rewrite dalam bahasa/tone/style KAMU
3. Bikin lebih engaging & opinionated
4. Max 280 karakter
5. Keep the essence, tapi buat lebih distinctive

OUTPUT (JSON):
{{
  "rewritten": "text post",
  "explanation": "kenapa gue rewrite kayak gini",
  "topics": ["topic1", "topic2"]
}}
"""

if __name__ == '__main__':
    # Demo: manual input
    example_post = "Polisi tangkap penipu Rp 2 miliar. Korban? 47 orang, semua kenalan dari Facebook."
    example_url = "https://x.com/NenkMonica/status/2073112858569957851"
    
    print("=== Copycat Mode: Manual Input ===\n")
    print(f"Original: {example_post}")
    print(f"URL: {example_url}\n")
    
    filepath = manual_input_post(example_post, example_url)
    print(f"Saved to: {filepath}\n")
    
    # Load voice profile
    voice_file = "vault/voice/profile.md"
    if os.path.exists(voice_file):
        with open(voice_file, 'r', encoding='utf-8') as f:
            voice = f.read()
    else:
        voice = "Sarcastic, witty, street-smart"
    
    prompt = generate_rewrite_prompt(example_post, voice)
    print("Generated prompt for LLM:")
    print(prompt[:500] + "...\n")
    
    print("Next step: Submit prompt to LLM (Hermes) untuk generate rewrite.")
