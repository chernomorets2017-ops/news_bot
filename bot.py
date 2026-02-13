import json
import hashlib
import time
from telegram import Bot
from config import BOT_TOKEN, CHANNEL, SIGN_LINK
from parser import get_news
from translator import translate

bot = Bot(BOT_TOKEN)

def load_db():
    try:
        return set(json.load(open("db.json")))
    except:
        return set()

def save_db(db):
    json.dump(list(db), open("db.json", "w"))

def hash_news(t):
    return hashlib.md5(t.encode()).hexdigest()

def main():
    db = load_db()
    news = get_news()

    for n in news:
        key = hash_news(n["title"])
        if key in db:
            continue

        title = translate(n["title"])
        text = translate(n["text"])[:1000]

        caption = f"""🌍 <b>{title}</b>

{text}

<a href="{SIGN_LINK}">.sup.news</a>
"""

        if n["img"]:
            bot.send_photo(CHANNEL, n["img"], caption=caption, parse_mode="HTML")
        else:
            bot.send_message(CHANNEL, caption, parse_mode="HTML")

        db.add(key)
        time.sleep(5)

    save_db(db)

if __name__ == "__main__":
    main()