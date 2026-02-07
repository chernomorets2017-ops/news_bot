import feedparser
import requests
import os
from bs4 import BeautifulSoup
import hashlib

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")

RSS = "https://news.google.com/rss/search?q=музыка+шоу+бизнес&hl=ru&gl=RU&ceid=RU:ru"
DB_FILE = "posted.txt"

def send_photo(text, image):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": CHANNEL, "caption": text, "parse_mode": "HTML"}, files={"photo": image})

def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML"})

def get_article(url):
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(p.text for p in soup.find_all("p")[:5])
    img = soup.find("meta", property="og:image")
    image = img["content"] if img else None
    return text, image

def summarize(text):
    return text[:450] + "..." if len(text) > 450 else text

def load_db():
    if not os.path.exists(DB_FILE):
        return set()
    return set(open(DB_FILE).read().splitlines())

def save_db(h):
    with open(DB_FILE, "a") as f:
        f.write(h + "\n")

posted = load_db()
feed = feedparser.parse(RSS)

for e in feed.entries[:1]:
    title = e.title
    link = e.link

    h = hashlib.md5(link.encode()).hexdigest()
    if h in posted:
        continue

    article_text, image = get_article(link)
    summary = summarize(article_text)

    post = f"<b>{title}</b>\n\n{summary}\n\n<a href='{link}'>Читать полностью</a>\n\n👉 <b>{CHANNEL_NAME}</b>"

    if image:
        send_photo(post, requests.get(image).content)
    else:
        send_text(post)

    save_db(h)