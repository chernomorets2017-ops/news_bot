# import feedparser
import telebot
import g4f
import requests
from bs4 import BeautifulSoup
import os
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK" 
DB_FILE = "last_links.txt"

SOURCES = [
    "https://tass.ru/rss/v2.xml",
    "https://www.kommersant.ru/RSS/news.xml",
    "https://lenta.ru/rss/last24",
    "https://www.rbc.ru/v10/rss/get/rbcnews.xml",
    "https://rt.com/rss/russian/"
]

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_links():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_posted_link(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def get_image(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        img = soup.find("meta", property="og:image")
        return img['content'] if img else None
    except:
        return None

def rewrite_text(title, text):
    prompt = f"Перескажи новость кратко для ТГ-канала. Используй жирный шрифт для заголовка. Пиши только текст новости, без приветствий. Текст: {title}. {text[:500]}"
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response
    except:
        return f"<b>{title}</b>\n\n{text[:300]}..."

def run():
    posted_links = get_posted_links()
    for url in SOURCES:
        feed = feedparser.parse(url)
        if not feed.entries:
            continue
        entry = feed.entries[0]
        link = entry.link
        if link in posted_links:
            continue 
        image_url = get_image(link)
        smart_text = rewrite_text(entry.title, entry.get('summary', ''))
        caption = f"{smart_text}\n\n<a href='{link}'>Источник</a>"
        try:
            if image_url:
                bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break 
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
