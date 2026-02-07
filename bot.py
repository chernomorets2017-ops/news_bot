import os
import json
import feedparser
from newspaper import Article
from telegram import Bot

# ==== SECRETS ====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # @username
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

# ==== SETTINGS ====
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=music+celebrity+news",
    "https://news.google.com/rss/search?q=show+business+news"
]

KEYWORDS = ["music", "song", "album", "singer", "rapper", "band", "concert", "celebrity", "музыка"]
POSTS_PER_RUN = 2
FALLBACK_IMAGE = "https://i.imgur.com/8Km9tLL.jpg"

bot = Bot(BOT_TOKEN)


# ====== DEDUP ======
def load_posted():
    try:
        with open("posted.json", "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_posted(urls):
    with open("posted.json", "w") as f:
        json.dump(list(urls), f)


# ====== SUMMARY ======
def summarize(text, max_len=450):
    text = text.replace("\n", " ")
    return text[:max_len] + "..." if len(text) > max_len else text


# ====== FETCH NEWS ======
def fetch_news():
    news = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:5]:
            news.append({"title": entry.title, "url": entry.link})
    return news


# ====== MAIN ======
def run():
    posted = load_posted()
    news = fetch_news()

    print("Found news:", len(news))

    sent = 0

    for item in news:
        if sent >= POSTS_PER_RUN:
            break

        if any(k in item["title"].lower() for k in KEYWORDS) is False:
            continue

        if item["url"] in posted:
            continue

        # Parse article
        try:
            article = Article(item["url"])
            article.download()
            article.parse()
            text = article.text
        except:
            continue

        summary = summarize(text)

        caption = f"<b>{item['title']}</b>\n\n{summary}\n\n<a href='{CHANNEL_LINK}'>Перейти в канал</a>"

        try:
            bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=FALLBACK_IMAGE,
                caption=caption,
                parse_mode="HTML"
            )
        except:
            bot.send_message(chat_id=CHANNEL_USERNAME, text=caption, parse_mode="HTML")

        posted.add(item["url"])
        sent += 1

    save_posted(posted)


if __name__ == "__main__":
    run()