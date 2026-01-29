import telebot
import g4f
import requests
import os
import re
from bs4 import BeautifulSoup

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916" 
CHANNEL_ID = "@SUP_V_BotK"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_posted_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header']): s.decompose()
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:3000]
    except:
        return None

def rewrite_text(title, content):
    # Жесткий промпт на краткость и структуру
    prompt = (
        f"Сделай краткий и четкий пересказ новости для ТГ-канала.\n"
        f"ЗАГОЛОВОК: {title}\n"
        f"ТЕКСТ: {content}\n\n"
        f"ФОРМАТ:\n"
        f"1. Жирный заголовок с эмодзи.\n"
        f"2. Суть новости (2-3 предложения).\n"
        f"3. Список ключевых фактов (3-4 пункта с эмодзи).\n"
        f"4. Итог (1 законченное предложение).\n\n"
        f"ПРАВИЛА: Не обрывай текст. Не пиши ссылки. Пиши кратко, но понятно."
    )
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.strip()
    except:
        return f"<b>{title}</b>\n\n{content[:500]}..."

def run():
    articles = requests.get(f"https://newsapi.org/v2/everything?q=(IT OR хайп OR технологии)&language=ru&apiKey={NEWS_API_KEY}").json().get('articles', [])
    posted = get_posted_links()

    for art in articles:
        if art['url'] in posted: continue
        
        full_text = get_full_text = get_full_article(art['url'])
        raw_content = full_text if (full_text and len(full_text) > 300) else art.get('description', "")
        
        if not raw_content: continue

        final_text = rewrite_text(art['title'], raw_content)
        caption = f"{final_text}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(art['url'])
            break
        except:
            continue

if __name__ == "__main__":
    run()
