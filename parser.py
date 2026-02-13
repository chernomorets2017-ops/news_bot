import feedparser
import requests
from bs4 import BeautifulSoup

FEEDS = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.theguardian.com/world/rss",
    "https://lenta.ru/rss/news",
    "https://www.rbc.ru/rss/news"
]

def get_full_text(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(p.text for p in soup.find_all("p"))
        return text[:3000]
    except:
        return ""

def get_news():
    result = []
    for f in FEEDS:
        feed = feedparser.parse(f)
        for e in feed.entries[:5]:
            title = e.title
            link = e.link
            full_text = get_full_text(link)

            if len(full_text) < 300:
                continue

            result.append({
                "title": title,
                "link": link,
                "text": full_text
            })
    return result