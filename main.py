import os
import telebot
import requests
from g4f.client import Client
import time

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
CHANNEL_ID = "@SUP_V_BotK"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)
client = Client()

def get_processed_links():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_link(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def rewrite_text(title, description):
    prompt = f"Перепиши новость для соцсетей. Сделай текст уникальным, коротким и хайповым. Используй эмодзи. Тема: {title}. Суть: {description}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"⚡️ {title}\n\n{description}"

def fetch_news():
    query = "politics OR music OR influencers OR tiktok OR youtube OR USA OR hollywood"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
    except:
        return

    processed = get_processed_links()
    
    for article in articles[:5]:
        link = article["url"]
        if link not in processed:
            title = article["title"]
            desc = article["description"] or ""
            
            final_text = rewrite_text(title, desc)
            message = f"{final_text}\n\n📎 {link}"
            
            try:
                bot.send_message(CHANNEL_ID, message)
                save_link(link)
                time.sleep(5)
            except:
                continue

if __name__ == "__main__":
    fetch_news()
