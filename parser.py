import feedparser
import requests
from bs4 import BeautifulSoup

FEEDS = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.theguardian.com/world/rss",
    "https://lenta.ru/rss/news"
]

def get_article(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

      
        text = " ".join(p.text for p in soup.find_all("p"))[:3000]

       
        img = ""
        og = soup.find("meta", property="og:image")
        if og:
            img = og["content"]

        return text, img
    except:
        return "", ""

def get_news():
    news = []
    for f in FEEDS:
        feed = feedparser.parse(f)
        for e in feed.entries[:5]:
            text, img = get_article(e.link)

            if len(text) < 400:
                continue

            news.append({
                "title": e.title,
                "text": text,
                "img": img
            })
    return news