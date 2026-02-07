import feedparser
import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")

RSS = "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru"

def send_photo(text, image):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": CHANNEL, "caption": text}, files={"photo": image})

def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text})

def get_image(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("meta", property="og:image")
        if img:
            return img["content"]
    except:
        return None

feed = feedparser.parse(RSS)

for e in feed.entries[:1]:
    title = e.title
    link = e.link

    image = get_image(link)

    post = f"📰 {title}\n\n🔗 {link}"

    if image:
        send_photo(post, requests.get(image).content)
    else:
        send_text(post)