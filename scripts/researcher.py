import feedparser
from datetime import datetime
import os

def scrape_rss_news(rss_urls):
    """Parse RSS feeds dari berbagai sumber news."""
    articles = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # Limit 10 per feed
                    media_url = None
                    # Coba ekstrak media dari entry.media_content atau entry.enclosures
                    if 'media_content' in entry and entry['media_content']:
                        media_url = entry['media_content'][0].get('url')
                    elif 'enclosures' in entry and entry['enclosures']:
                        media_url = entry['enclosures'][0].get('url')

                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', '#'),
                        'summary': entry.get('summary', 'No summary').replace('<p>', '').replace('</p>', ''),
                        'source': feed.feed.get('title', 'Unknown Source'),
                        'media_url': media_url  # Tambahkan media_url di sini
                    })
        except Exception as e:
            print(f"Error parsing {url}: {e}")
    return articles

def save_to_vault(articles, topic):
    today = datetime.now().strftime('%Y-%m-%d')
    folder_path = f"vault/research/{today}"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{topic}.md")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {topic.replace('-', ' ').title()} - {today}\n\n")
        for article in articles:
            f.write(f"## [{article['title']}]({article['link']})\n")
            f.write(f"- Source: {article['source']}\n")
            f.write(f"- Summary: {article['summary'][:200]}...\n")
            if article['media_url']: # Tulis media_url jika ada
                f.write(f"- Media: {article['media_url']}\n")
            f.write("\n") # Baris kosong untuk pemisah
    return file_path

if __name__ == '__main__':
    # RSS feeds untuk viral content, crime, gossip Indonesia
    rss_feeds = [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.cnnindonesia.com/rss/feeds.xml",
        "https://feeds.detik.com/detik/index",
    ]
    
    articles = scrape_rss_news(rss_feeds)
    if articles:
        saved_file = save_to_vault(articles, "daily-news")
        print(f"Saved {len(articles)} articles to {saved_file}")
    else:
        print("No articles found")
