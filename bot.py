from telegram import Bot
from parser import get_news
import json
import time
from config import BOT_TOKEN, CHANNEL, SIGN

bot = Bot(BOT_TOKEN)

def load_posted():
    try:
        with open("posted.json") as f:
            return json.load(f)
    except:
        return []

def save_posted(data):
    with open("posted.json", "w") as f:
        json.dump(data, f)

posted = load_posted()

while True:
    news = get_news()
    for n in news:
        if n["title"] in posted:
            continue

        text = f"🌍 Мир\n\n{n['title']}\n\n{.sup.news}\n{SIGN}"

        bot.send_message(CHANNEL, text)
        posted.append(n["title"])
        save_posted(posted)

        time.sleep(10)

    time.sleep(3600)