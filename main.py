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

def rewrite_text_and_format(title, description, link):
    prompt = f"""
    Напиши хайповый пост для ТГ-канала.
    Тема: {title}
    Суть: {description}
    
    Правила:
    1. 3 коротких абзаца.
    2. Первый абзац — ЖИРНЫМ (заголовок-молния).
    3. Добавляй тематические эмодзи-стикеры в начале и конце каждого абзаца (например, 🎸 для музыки, 🇺🇸 для США, 📱 для соцсетей).
    4. Текст должен быть уникальным и полностью пересказывать суть.
    5. В конце фраза: [Читать оригинал]({link})
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"⚡️ **{title}**\n\n{description}\n\n[Читать оригинал]({link})"

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
            img = article.get("urlToImage")
            
            content = rewrite_text_and_format(title, desc, link)
            
            try:
                if img and img.startswith("http"):
                    bot.send_photo(CHANNEL_ID, img, caption=content, parse_mode='Markdown')
                else:
                    bot.send_message(CHANNEL_ID, content, parse_mode='Markdown')
                save_link(link)
                time.sleep(10)
            except:
                continue

if __name__ == "__main__":
    fetch_news()
