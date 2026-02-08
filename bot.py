import os, json, requests
from parser import get_articles
from sources import SOURCES
from categories import CATEGORIES, KEYWORDS

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")

def load_db():
    try:
        return json.load(open("db.json"))
    except:
        return []

def save_db(data):
    json.dump(data, open("db.json", "w"))

def detect_category(text):
    t = text.lower()
    for cat, words in KEYWORDS.items():
        for w in words:
            if w.lower() in t:
                return CATEGORIES[cat]
    return CATEGORIES["world"]

def send_photo(title, img):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    text = f"{title}\n\n.sup.news"
    requests.post(url, json={
        "chat_id": CHANNEL_NAME,
        "photo": img,
        "caption": text
    })

def send_text(title):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"{title}\n\n.sup.news"
    requests.post(url, json={
        "chat_id": CHANNEL_NAME,
        "text": text
    })

def main():
    db = load_db()

    for src in SOURCES:
        for art in get_articles(src):
            if art["title"] in db:
                continue

            db.append(art["title"])
            if len(db) > 500:
                db = db[-500:]

            cat = detect_category(art["title"])
            title = f"{cat}\n\n{art['title']}"

            if art["image"]:
                send_photo(title, art["image"])
            else:
                send_text(title)

    save_db(db)

if __name__ == "__main__":
    main()