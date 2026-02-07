import feedparser
import requests
from bs4 import BeautifulSoup
from config import BOT_TOKEN, CHANNEL, RSS_URL

def get_image(url):
    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("meta", property="og:image")
        if img:
            return img["content"]
    except:
        return None

def send_post(title, link, image):
    channel_link = f"https://t.me/{CHANNEL.replace('@','')}"

    text = f"<b>{title}</b>\n\n<a href='{channel_link}'>Читать полностью</a>"

    api = f"https://api.telegram.org/bot{BOT_TOKEN}"

    if image:
        data = {
            "chat_id": CHANNEL,
            "photo": image,
            "caption": text,
            "parse_mode": "HTML"
        }
        requests.post(api + "/sendPhoto", data=data)
    else:
        data = {
            "chat_id": CHANNEL,
            "text": text,
            "parse_mode": "HTML"
        }
        requests.post(api + "/sendMessage", data=data)

def main():
    feed = feedparser.parse(RSS_URL)
    entry = feed.entries[0]

    title = entry.title
    link = entry.link
    image = get_image(link)

    send_post(title, link, image)

if __name__ == "__main__":
    main()