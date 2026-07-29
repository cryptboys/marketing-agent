import subprocess
import json
import os
from datetime import datetime

def scrape_twitter_user(username, max_posts=5):
    """Scrape tweets from a Twitter user using snscrape."""
    command = [
        "snscrape",
        "--jsonl",
        "--progress",
        "twitter-user",
        username
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    
    if error:
        print(f"Error scraping {username}: {error.decode()}")
        return []

    tweets = []
    for line in output.decode().splitlines():
        if line.strip():
            try:
                tweet = json.loads(line)
                tweets.append(tweet)
                if len(tweets) >= max_posts:
                    break
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} in line: {line}")
    return tweets

def save_copycat_posts(tweets, username):
    """Save scraped tweets to vault/research/copycat/"""
    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join("vault/research/copycat", today)
    os.makedirs(folder_path, exist_ok=True)
    
    filepath = os.path.join(folder_path, f"{username}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Copycat Posts from @{username} - {today}\n\n")
        for i, tweet in enumerate(tweets):
            f.write(f"## Post {i+1}\n")
            f.write(f"URL: {tweet.get('url', '#')}\n")
            f.write(f"Date: {tweet.get('date', 'N/A')}\n")
            f.write(f"Content:\n```\n{tweet.get('content', '')}\n```\n\n")
    return filepath

if __name__ == "__main__":
    target_users = ["NenkMonica", "LambeSahamjja"]
    
    for user in target_users:
        print(f"Scraping posts from @{user}...")
        tweets = scrape_twitter_user(user, max_posts=5)
        if tweets:
            saved_file = save_copycat_posts(tweets, user)
            print(f"Saved {len(tweets)} posts to {saved_file}")
        else:
            print(f"No posts found for @{user}")
