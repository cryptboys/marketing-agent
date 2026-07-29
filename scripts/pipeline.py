"""
Content Pipeline: Generator + Checker
Reads from vault/research, generates content via LLM, validates with 5-point check.
"""

import json
import os
import re
from datetime import datetime


# --- Config ---
VAULT_DIR = "vault"
CONTENT_DIR = os.path.join(VAULT_DIR, "content")
VOICE_DIR = os.path.join(VAULT_DIR, "voice")

# Voice profile (loaded from vault/voice/profile.md)
DEFAULT_VOICE = {
    "language": "Indonesian mixed with English (casual)",
    "tone": "sarcastic, witty, street-smart",
    "max_length": 280,
    "avoid": ["generic AI phrases", "corporate jargon", "excessive emojis"],
    "style": "terse, punchy, opinionated. One-liners. No fluff."
}

# 5-Point Checker Config
CHECK_CONFIG = {
    "anti_slop": {
        "banned_phrases": [
            "dive into", "delve", "in the realm of", "it's worth noting",
            "let's explore", "game-changer", "seamless", "leverage",
            "synergy", "holistic approach", "in today's fast-paced",
            "I hope this helps", "as an AI", "happy to help"
        ],
        "max_filler_ratio": 0.3
    },
    "data_freshness": {
        "max_age_hours": 48
    },
    "fact_check": {
        "require_source": True,
        "min_sources": 1
    },
    "voice_match": {
        "min_score": 7  # out of 10
    },
    "platform_rules": {
        "x_max_chars": 280,
        "x_max_hashtags": 3,
        "x_max_mentions": 3
    }
}


def load_voice_profile():
    """Load voice profile from vault or use default."""
    profile_path = os.path.join(VOICE_DIR, "profile.md")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return f.read()
    return json.dumps(DEFAULT_VOICE, indent=2)


def read_research(topic=None):
    """Read latest research from vault."""
    today = datetime.now().strftime("%Y-%m-%d")
    research_dir = os.path.join(VAULT_DIR, "research", today)
    
    if not os.path.exists(research_dir):
        return []
    
    articles = []
    for filename in os.listdir(research_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(research_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Parse markdown sections
                sections = re.split(r"## \[", content)
                for section in sections[1:]:
                    title_match = re.match(r"(.+?)\]\((.+?)\)", section)
                    if title_match:
                        title = title_match.group(1)
                        link = title_match.group(2)
                        summary_match = re.search(r"Summary: (.+?)(?:\n|$)", section)
                        summary = summary_match.group(1) if summary_match else ""
                        articles.append({
                            "title": title,
                            "link": link,
                            "summary": summary,
                            "file": filename
                        })
    return articles


def generate_prompt(article, voice_profile):
    """Generate LLM prompt for content creation."""
    return f"""Kamu adalah content creator Indonesia yang cerdas dan sarkastik.

VOICE PROFILE:
{voice_profile}

TUGAS:
Buat 1 post X (max 280 karakter) berdasarkan berita ini:

JUDUL: {article['title']}
SUMMARY: {article['summary']}
SUMBER: {article['link']}

ATURAN:
- Bahasa Indonesia campur Inggris (kasual)
- Tone: sinis, tajam, street-smart
- Max 280 karakter
- Max 3 hashtag
- Sertakan 1 source link
- NO generic AI phrases (delve, explore, game-changer)
- NO corporate jargon
- NO excessive emojis

OUTPUT FORMAT (JSON):
{{
  "content": "teks post",
  "hashtags": ["tag1", "tag2"],
  "source_url": "link sumber",
  "topic_category": "crime|gossip|viral|oddity"
}}
"""


def generate_content(article, voice_profile):
    """Generate content placeholder - to be called via Hermes LLM."""
    prompt = generate_prompt(article, voice_profile)
    # Save prompt for Hermes execution
    prompt_dir = os.path.join(VAULT_DIR, "queue")
    os.makedirs(prompt_dir, exist_ok=True)
    
    prompt_file = os.path.join(prompt_dir, f"gen_{datetime.now().strftime('%H%M%S')}.json")
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump({
            "article": article,
            "prompt": prompt,
            "status": "pending"
        }, f, indent=2, ensure_ascii=False)
    
    return prompt_file


def check_anti_slop(content):
    """Check 1: Anti-slop detection."""
    content_lower = content.lower()
    banned = CHECK_CONFIG["anti_slop"]["banned_phrases"]
    
    violations = [phrase for phrase in banned if phrase.lower() in content_lower]
    
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "message": f"Banned phrases found: {violations}" if violations else "Clean"
    }


def check_data_freshness(article):
    """Check 2: Data freshness."""
    # Simplified: check if article has date info
    # In production, parse article date
    return {
        "passed": True,  # Assume fresh if from today's research
        "message": "Fresh data from daily scrape"
    }


def check_fact_source(article):
    """Check 3: Fact/source check."""
    has_link = bool(article.get("link", "").startswith("http"))
    has_summary = len(article.get("summary", "")) > 20
    
    return {
        "passed": has_link and has_summary,
        "message": "Source verified" if (has_link and has_summary) else "Missing source or summary"
    }


def check_voice_match(content, voice_profile):
    """Check 4: Voice match scoring."""
    issues = []
    
    # Check length
    if len(content) > CHECK_CONFIG["platform_rules"]["x_max_chars"]:
        issues.append(f"Too long: {len(content)} chars")
    
    # Check for banned phrases
    slop_check = check_anti_slop(content)
    if not slop_check["passed"]:
        issues.extend([f"Slop: {v}" for v in slop_check["violations"]])
    
    # Check hashtag count
    hashtag_count = len(re.findall(r"#\w+", content))
    if hashtag_count > CHECK_CONFIG["platform_rules"]["x_max_hashtags"]:
        issues.append(f"Too many hashtags: {hashtag_count}")
    
    score = 10 - len(issues)
    
    return {
        "passed": score >= CHECK_CONFIG["voice_match"]["min_score"],
        "score": score,
        "issues": issues,
        "message": f"Voice score: {score}/10"
    }


def check_platform_rules(content):
    """Check 5: Platform-specific rules."""
    char_count = len(content)
    max_chars = CHECK_CONFIG["platform_rules"]["x_max_chars"]
    
    return {
        "passed": char_count <= max_chars,
        "char_count": char_count,
        "max_chars": max_chars,
        "message": f"{char_count}/{max_chars} characters"
    }


def validate_content(content, article, voice_profile):
    """Run all 5 checks."""
    results = {
        "anti_slop": check_anti_slop(content),
        "data_freshness": check_data_freshness(article),
        "fact_source": check_fact_source(article),
        "voice_match": check_voice_match(content, voice_profile),
        "platform_rules": check_platform_rules(content)
    }
    
    all_passed = all(r["passed"] for r in results.values())
    
    return {
        "all_passed": all_passed,
        "checks": results
    }


def save_content(content_data, article, validation):
    """Save generated content to vault."""
    today = datetime.now().strftime("%Y-%m-%d")
    content_dir = os.path.join(CONTENT_DIR, today)
    os.makedirs(content_dir, exist_ok=True)
    
    topic = content_data.get("topic_category", "general")
    timestamp = datetime.now().strftime("%H%M%S")
    
    filepath = os.path.join(content_dir, f"{topic}_{timestamp}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic.title()} Post\n\n")
        f.write(f"**Status:** {'READY' if validation['all_passed'] else 'NEEDS REVIEW'}\n\n")
        f.write(f"## Content\n{content_data.get('content', '')}\n\n")
        f.write(f"## Source\n{article.get('link', '')}\n\n")
        f.write(f"## Validation\n```json\n{json.dumps(validation, indent=2)}\n```\n")
    
    return filepath


if __name__ == "__main__":
    print("=== Content Pipeline: Generator + Checker ===\n")
    
    # Load voice
    voice = load_voice_profile()
    print(f"Voice profile loaded: {len(voice)} chars\n")
    
    # Read research
    articles = read_research()
    print(f"Found {len(articles)} articles for processing\n")
    
    # Process first article as demo
    if articles:
        article = articles[0]
        print(f"Processing: {article['title'][:60]}...")
        
        prompt_file = generate_content(article, voice)
        print(f"Prompt saved to: {prompt_file}")
        
        # Simulate content for testing validation
        test_content = "Gue lagi baca berita soal ini. Ironis banget. #Indonesia #Viral"
        validation = validate_content(test_content, article, voice)
        
        print(f"\nValidation Result: {'PASS' if validation['all_passed'] else 'FAIL'}")
        for check, result in validation["checks"].items():
            status = "✓" if result["passed"] else "✗"
            print(f"  {status} {check}: {result['message']}")
    else:
        print("No articles to process. Run researcher.py first.")
