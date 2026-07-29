import requests
from bs4 import BeautifulSoup

url = "https://news.google.com/search?q=indonesia&hl=en-US&gl=US&ceid=US:en"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
articles = soup.find_all('article')
print(f"Total articles element: {len(articles)}")
for a in articles[:5]:
    # find all a tag inside article
    a_tags = a.find_all('a')
    for tag in a_tags:
        if tag.text:
            print("Title:", tag.text)
            print("Link:", tag.get('href'))
            break
