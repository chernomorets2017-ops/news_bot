import json
import time
import hashlib
from telegram import Bot
from config import BOT_TOKEN, CHANNEL, SIGN_LINK
from parser import get_news
from ai_summarizer import summarize

bot = Bot(BOT_TOKEN)

def load_db():
    try:
        with open("db.json") as f:
            return set(json.load(f))
    except:
        return set()

def save_db(db):
    with open("db.json", "w") as f:
        json.dump(list(db), f)

def hash_news(title):
    return hashlib.md5(title.encode()).hexdigest()

def format_post(title, link, summary):
    return f"""🌍 <b>{title}</b>

🧠 {summary}


<a href="{SIGN_LINK}">.sup.news</a>
"""

def main():
    db = load_db()
    news = get_news()

    for n in news:
        key = hash_news(n["title"])
        if key in db:
            continue

        summary = summarize(n["summary"])
        text = format_post(n["title"], n["link"], summary)

        bot.send_message(
            CHANNEL,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=False
        )

        db.add(key)
        time.sleep(4)

    save_db(db)

if __name__ == "__main__":
    main()