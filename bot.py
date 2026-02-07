import os
import feedparser
import hashlib
import json
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

bot = Bot(BOT_TOKEN)

KEYWORDS = [
    "music", "song", "album", "singer", "rapper", "band",
    "concert", "tour", "festival",
    "celebrity", "showbiz", "entertainment", "pop", "hip hop",
    "Grammy", "Billboard", "Spotify"
]

DB_FILE = "posted.json"

def load_db():
    if os.path.exists(DB_FILE):
        return json.load(open(DB_FILE))
    return []

def save_db(db):
    json.dump(db, open(DB_FILE, "w"))

posted = load_db()

feed = feedparser.parse("https://news.google.com/rss?hl=en&gl=US&ceid=US:en")

for entry in feed.entries[:10]:
    title = entry.title
    summary = entry.get("summary", "")
    link = entry.link

    text_check = (title + summary).lower()

    # мягкий фильтр
    if not any(k in text_check for k in KEYWORDS):
        continue

    # анти-дубликат
    uid = hashlib.md5(link.encode()).hexdigest()
    if uid in posted:
        continue

    posted.append(uid)
    save_db(posted)

    # короткий пересказ (упрощенный)
    short = summary[:400]

    message = f"""<b>{title}</b>

{short}...

<a href="{link}">Читать полностью</a>

<a href="{CHANNEL_LINK}">Подписаться на канал</a>"""

    bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode="HTML")
    break