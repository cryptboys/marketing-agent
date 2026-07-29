import requests
from bs4 import BeautifulSoup

def scrape_nitter(username):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # Coba beberapa instance Nitter
    instances = [
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
        "https://nitter.cz"
    ]
    
    for instance in instances:
        url = f"{instance}/{username}"
        try:
            print(f"Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                tweets = []
                for tweet in soup.select('.timeline-item'):
                    content_tag = tweet.select_one('.tweet-content')
                    if content_tag:
                        tweets.append(content_tag.text.strip())
                if tweets:
                    return tweets
        except Exception as e:
            print(f"Failed {instance}: {e}")
    return []

if __name__ == '__main__':
    for user in ["NenkMonica", "LambeSahamjja"]:
        print(f"Scraping {user}...")
        tweets = scrape_nitter(user)
        print(f"Result {user}: {tweets[:3]}")
