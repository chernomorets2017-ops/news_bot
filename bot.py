import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from deep_translator import GoogleTranslator
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")

bot = Bot(TOKEN)

RSS = "https://news.google.com/rss?hl=en&gl=US&ceid=US:en"
DB_FILE = "posted.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return []
    return json.load(open(DB_FILE))


def save_db(data):
    json.dump(data, open(DB_FILE, "w"))


def get_article(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        img = soup.find("meta", property="og:image")
        image = img["content"] if img else None

        paragraphs = soup.find_all("p")
        text = " ".join(p.text for p in paragraphs[:3])

        return image, text
    except:
        return None, ""


def translate(text):
    try:
        return GoogleTranslator(source="auto", target="ru").translate(text)
    except:
        return text


def post_news():
    feed = feedparser.parse(RSS)
    posted = load_db()

    for entry in feed.entries[:3]:
        if entry.link in posted:
            continue

        title = translate(entry.title)
        link = entry.link

        image, article_text = get_article(link)
        article_text = translate(article_text[:1000])

        msg = f"""📰 <b>{title}</b>

{article_text}

<a href="https://t.me/{CHANNEL[1:]}">👉 Читать в @{CHANNEL[1:]}</a>
"""

        if image:
            bot.send_photo(CHANNEL, image, caption=msg, parse_mode="HTML")
        else:
            bot.send_message(CHANNEL, msg, parse_mode="HTML")

        posted.append(entry.link)
        save_db(posted)


post_news()