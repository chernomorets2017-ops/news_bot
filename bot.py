import os
import json
import feedparser
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=music+celebrity+news",
]

KEYWORDS = ["music", "album", "song", "singer", "rapper", "band"]
POSTS_PER_RUN = 2
FALLBACK_IMAGE = "https://i.imgur.com/8Km9tLL.jpg"

bot = Bot(BOT_TOKEN)


def load_posted():
    try:
        return set(json.load(open("posted.json")))
    except:
        return set()


def save_posted(urls):
    json.dump(list(urls), open("posted.json", "w"))


def run():
    posted = load_posted()
    sent = 0

    for feed in RSS_FEEDS:
        data = feedparser.parse(feed)

        for e in data.entries:
            if sent >= POSTS_PER_RUN:
                break

            title = e.title
            link = e.link
            summary = e.summary if "summary" in e else ""

            if any(k in title.lower() for k in KEYWORDS) is False:
                continue
            if link in posted:
                continue

            text = f"<b>{title}</b>\n\n{summary[:400]}...\n\n<a href='{CHANNEL_LINK}'>Channel</a>"

            bot.send_photo(chat_id=CHANNEL_USERNAME, photo=FALLBACK_IMAGE, caption=text, parse_mode="HTML")

            posted.add(link)
            sent += 1

    save_posted(posted)


if __name__ == "__main__":
    run()