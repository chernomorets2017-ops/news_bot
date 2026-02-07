import os
import time
import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")

bot = Bot(token=BOT_TOKEN)

RSS_FEED = "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru"

posted = set()

def get_image(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og["content"]:
            return og["content"]
    except:
        pass
    return None


def send_news():
    feed = feedparser.parse(RSS_FEED)

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link

        if link in posted:
            continue
        posted.add(link)

        img = get_image(link)

        text = f"📰 *{title}*\n\n🔗 [Читать полностью]({link})"

        try:
            if img:
                bot.send_photo(chat_id=CHANNEL_NAME, photo=img, caption=text, parse_mode="Markdown")
            else:
                bot.send_message(chat_id=CHANNEL_NAME, text=text, parse_mode="Markdown")
        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    print("BOT RUNNING")
    send_news()