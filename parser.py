import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib
import os

SENT_FILE = "sent.txt"

# load sent
if os.path.exists(SENT_FILE):
    with open(SENT_FILE) as f:
        SENT = set(f.read().splitlines())
else:
    SENT = set()

def save_hash(h):
    with open(SENT_FILE, "a") as f:
        f.write(h + "\n")

def is_duplicate(text):
    h = hashlib.md5(text.encode()).hexdigest()
    if h in SENT:
        return True
    SENT.add(h)
    save_hash(h)
    return False

def extract_article(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # image
        img = None
        og = soup.find("meta", property="og:image")
        if og:
            img = og["content"]

        # text
        paragraphs = [p.text for p in soup.find_all("p")]
        text = " ".join(paragraphs)[:1500]

        return text, img
    except:
        return "", None


def get_news():
    feed = feedparser.parse("https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru")

    result = []

    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link

        article_text, image = extract_article(link)
        if len(article_text) < 300:
            continue

        full_text = title + article_text
        if is_duplicate(full_text):
            continue

        result.append({
            "title": title,
            "text": article_text[:700],
            "img": image,
            "link": link
        })

    return result