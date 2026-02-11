import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib
import os

SENT_FILE = "sent.txt"


if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_cache = set(f.read().splitlines())
else:
    sent_cache = set()


def save_hash(h):
    with open(SENT_FILE, "a") as f:
        f.write(h + "\n")


def is_duplicate(text):
    h = hashlib.md5(text.encode()).hexdigest()
    if h in sent_cache:
        return True
    sent_cache.add(h)
    save_hash(h)
    return False


def is_trash(text):
    if len(text) < 150:
        return True

    trash = [
        "Прочтите о нашем подходе",
        "Advertisement",
        "Subscribe",
        "Подробнее по ссылке",
        "Read more"
    ]
    return any(t.lower() in text.lower() for t in trash)


def translate_ru(text):
   
    try:
        import googletrans
        translator = googletrans.Translator()
        return translator.translate(text, dest="ru").text
    except:
        return text


def get_news():
    url = "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru"
    feed = feedparser.parse(url)

    news_list = []

    for entry in feed.entries[:5]:
        title = entry.title
        summary = BeautifulSoup(entry.summary, "html.parser").text

        text = f"{title}\n\n{summary}"

        if is_trash(text):
            continue

        if is_duplicate(text):
            continue

        news_list.append({
            "title": title,
            "text": summary,
            "link": entry.link
        })

    return news_list