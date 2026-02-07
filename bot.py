import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_USERNAME")

RSS = "https://news.google.com/rss"

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHANNEL, "text": text})
    print(r.text)

print("BOT STARTED")
send("BOT STARTED")

feed = feedparser.parse(RSS)
print("RSS ITEMS:", len(feed.entries))

if len(feed.entries) > 0:
    e = feed.entries[0]
    msg = f"{e.title}\n{e.link}"
    send(msg)