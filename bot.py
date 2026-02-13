import json
import time
from telegram import Bot
from config import BOT_TOKEN, CHANNEL
from parser import get_news

bot = Bot(BOT_TOKEN)

def load_posted():
    try:
        with open("posted.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_posted(posted):
    with open("posted.json", "w") as f:
        json.dump(list(posted), f)

def main():
    posted = load_posted()
    news = get_news()

    for item in news:
        if item in posted:
            continue
        
        bot.send_message(CHANNEL, item)
        posted.add(item)
        time.sleep(3)

    save_posted(posted)

if __name__ == "__main__":
    main()