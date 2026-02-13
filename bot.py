import json
import time
import hashlib
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

def hash_news(text):
    return hashlib.md5(text.encode()).hexdigest()

def format_post(title, text, link):
    return f"""🌍 <b>{title}</b>

{text[:1000]}

🔗 <a href="{link}">Читать полностью</a>

<a href="{SIGN_LINK}">.sup.news</a>
"""

def main():
    db = load_db()
    news = get_news()

    for n in news:
        key = hash_news(n["title"])
        if key in db:
            continue

        title = translate(n["title"])
        text = translate(n["text"])

        if len(text) < 200:
            continue

        post = format_post(title, text, n["link"])

        bot.send_message(CHANNEL, post, parse_mode="HTML", disable_web_page_preview=False)
        db.add(key)
        time.sleep(5)

    save_db(db)

if __name__ == "__main__":
    main()