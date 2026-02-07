import os
import json
import feedparser
import random
from telegram import Bot

# ===== СЕКРЕТЫ =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # @yourchannel
CHANNEL_LINK = os.getenv("CHANNEL_LINK")          # https://t.me/yourchannel

# ===== НАСТРОЙКИ =====
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=music+celebrity+news&hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=show+business+news&hl=en&gl=US&ceid=US:en"
]

KEYWORDS = ["music", "album", "song", "singer", "rapper", "band", "celebrity", "concert"]
POSTS_PER_RUN = 2

IMAGES = [
    "https://i.imgur.com/8Km9tLL.jpg",
    "https://i.imgur.com/Z6X9Z9s.jpg",
    "https://i.imgur.com/1c9a1aF.jpg"
]

bot = Bot(BOT_TOKEN)


# ===== АНТИ-ДУБЛИКАТЫ =====
def load_posted():
    try:
        return set(json.load(open("posted.json")))
    except:
        return set()

def save_posted(data):
    json.dump(list(data), open("posted.json", "w"))


# ===== ОСНОВНАЯ ЛОГИКА =====
def run():
    posted = load_posted()
    sent = 0

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for e in feed.entries:
            if sent >= POSTS_PER_RUN:
                break

            title = e.title
            link = e.link
            summary = e.summary if "summary" in e else ""

            text_lower = (title + summary).lower()

            # фильтр по теме
            if not any(k in text_lower for k in KEYWORDS):
                continue

            # анти-дубликат
            if link in posted:
                continue

            # короткий пересказ
            summary = summary.replace("<b>", "").replace("</b>", "")
            summary = summary.replace("<a", "").replace("</a>", "")
            summary = summary[:450]

            text = f"""<b>{title}</b>

{summary}...

<a href="{CHANNEL_LINK}">Подписаться на канал</a>"""

            image = random.choice(IMAGES)

            bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=image,
                caption=text,
                parse_mode="HTML"
            )

            posted.add(link)
            sent += 1

    save_posted(posted)


if __name__ == "__main__":
    run()