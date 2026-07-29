import argparse
import json
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Import dari module pipeline kita
sys.path.append('scripts')
from copycat_manual import manual_input_post, generate_rewrite_prompt
from pipeline import (
    load_voice_profile, 
    validate_content, 
    save_content,
    check_anti_slop,
    check_voice_match,
    check_platform_rules
)

def rewrite_with_llm(prompt):
    """
    Placeholder untuk LLM call via Hermes.
    Dalam production, ini akan dipanggil via Hermes LLM API.
    Untuk demo, return mock rewrite.
    """
    # TODO: Integrate dengan Hermes LLM
    # Untuk sekarang, return mock result
    return {
        "rewritten": "Penipu Rp 2M ditangkap. 47 korban, semua dari FB. Trust issues much? 💀 #Indonesia #Crime",
        "explanation": "Rewrite lebih sinis dan compact, tambah sarcasm + emoji minimal.",
        "topics": ["crime", "scam"]
    }

def publish_to_twitter(content, media_path=None, cookies_path="secrets/twitter_cookies.json"):
    """
    Publish ke X menggunakan twitter-cli + cookies.
    TODO: Implement actual twitter-cli integration.
    """
    print(f"[PUBLISH] Would post to X: {content}")
    if media_path:
        print(f"[PUBLISH] Would attach media: {media_path}")
    # Placeholder: actual implementation butuh twitter-cli wrapper
    return {"status": "success", "tweet_id": "mock_12345"}

def fetch_media_from_url(post_url):
    """Coba ekstrak og:image/og:video dari meta tag dan download."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(post_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        media_url = None
        # Prioritas: og:image, twitter:image, og:video
        og_image = soup.find('meta', property='og:image')
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        og_video = soup.find('meta', property='og:video')
        
        if og_image and og_image.get('content'):
            media_url = og_image['content']
        elif twitter_image and twitter_image.get('content'):
            media_url = twitter_image['content']
        elif og_video and og_video.get('content'):
            media_url = og_video['content']
            
        if media_url:
            print(f"  [MEDIA] Found media URL: {media_url}")
            # Download media
            media_response = requests.get(media_url, timeout=10)
            if media_response.status_code == 200:
                ext = media_url.split('.')[-1].split('?')[0] # Get extension from URL
                if len(ext) > 4: ext = 'jpg' # fallback for long extensions
                filename = f"media_{datetime.now().strftime('%H%M%S')}.{ext}"
                media_path = os.path.join("vault/media_cache", filename)
                os.makedirs("vault/media_cache", exist_ok=True)
                with open(media_path, 'wb') as f:
                    f.write(media_response.content)
                print(f"  [MEDIA] Downloaded to: {media_path}")
                return media_path
            else:
                print(f"  [MEDIA] Failed to download media: {media_response.status_code}")
        else:
            print("  [MEDIA] No media meta tag found.")
            
    except Exception as e:
        print(f"  [MEDIA] Error fetching media: {e}")
    return None

def run_copycat_pipeline(raw_text, source_url):
    """End-to-end copycat pipeline."""
    print("=== COPYCAT PIPELINE ===\n")
    
    # Stage 1: Save raw input
    print("[1/5] Saving raw input...")
    saved_file = manual_input_post(raw_text, source_url)
    print(f"✓ Saved: {saved_file}\n")

    # Stage 1.5: Fetch Media
    print("[1.5/5] Fetching media from source URL...")
    media_path = fetch_media_from_url(source_url)
    if media_path:
        print(f"✓ Media fetched: {media_path}\n")
    else:
        print("✗ No media found or failed to fetch.\n")
    
    # Stage 2: Generate rewrite prompt
    print("[2/5] Loading voice & generating prompt...")
    voice = load_voice_profile()
    prompt = generate_rewrite_prompt(raw_text, voice)
    print(f"✓ Prompt ready ({len(prompt)} chars)\n")
    
    # Stage 3: LLM Rewrite
    print("[3/5] Rewriting via LLM...")
    rewrite_result = rewrite_with_llm(prompt)
    rewritten = rewrite_result["rewritten"]
    print(f"✓ Rewritten: {rewritten}\n")
    
    # Stage 4: Validation (5-point check)
    print("[4/5] Running validation (5-point check)...")
    validation = validate_content(rewritten, {"link": source_url, "summary": raw_text}, voice)
    
    for check, result in validation["checks"].items():
        status = "✓" if result["passed"] else "✗"
        print(f"  {status} {check}: {result['message']}")
    
    if not validation["all_passed"]:
        print("\n⚠ Validation FAILED. Review needed.")
        return None
    
    print("\n✓ All checks passed!\n")
    
    # Stage 5: Publish
    print("[5/5] Publishing to X...")
    publish_result = publish_to_twitter(rewritten, media_path=media_path)
    print(f"✓ Published: {publish_result}\n")
    
    # Save final content
    content_data = {
        "content": rewritten,
        "topic_category": rewrite_result["topics"][0] if rewrite_result["topics"] else "general",
        "source_url": source_url,
        "media_path": media_path
    }
    final_file = save_content(content_data, {"link": source_url}, validation)
    print(f"✓ Final content saved: {final_file}")
    
    return {
        "rewritten": rewritten,
        "validation": validation,
        "publish": publish_result,
        "saved_to": final_file
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Content Pipeline Orchestration')
    parser.add_argument('--mode', type=str, default='copycat', help='Pipeline mode (copycat)')
    parser.add_argument('--input', type=str, required=True, help='Raw post text')
    parser.add_argument('--url', type=str, required=True, help='Source X.com URL')
    
    args = parser.parse_args()
    
    if args.mode == 'copycat':
        result = run_copycat_pipeline(args.input, args.url)
        if result:
            print("\n✅ PIPELINE COMPLETE")
        else:
            print("\n❌ PIPELINE FAILED")
            sys.exit(1)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)
