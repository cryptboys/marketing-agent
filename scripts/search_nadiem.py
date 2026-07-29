import feedparser
import urllib.parse
from datetime import datetime
import os

def search_news(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=id&gl=ID&ceid=ID:id"
    print(f"Fetching: {url}")
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:5]:
        media_url = None
        if 'media_content' in entry and entry['media_content']:
            media_url = entry['media_content'][0].get('url')
        elif 'enclosures' in entry and entry['enclosures']:
            media_url = entry['enclosures'][0].get('url')
            
        articles.append({
            'title': entry.get('title', 'No title'),
            'link': entry.get('link', '#'),
            'summary': entry.get('summary', 'No summary'),
            'source': entry.get('source', {}).get('title', 'Google News'),
            'media_url': media_url
        })
    return articles

if __name__ == '__main__':
    query = "putusan pengadilan nadiem makarim"
    articles = search_news(query)
    print(f"Found {len(articles)} articles.")
    for idx, a in enumerate(articles):
        print(f"\n[{idx+1}] {a['title']}")
        print(f"Link: {a['link']}")
        print(f"Source: {a['source']}")
        print(f"Media: {a['media_url']}")
