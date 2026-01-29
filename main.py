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
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']): s.decompose()
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:3500]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Сделай четкий пересказ новости. БЕЗ МНОГОТОЧИЙ В КОНЦЕ. БЕЗ ОБРЫВОВ.\n"
        f"НОВОСТЬ: {title}\n"
        f"ТЕКСТ: {content}\n\n"
        f"ФОРМАТ:\n"
        f"1. ⚡️ Жирный заголовок.\n"
        f"2. Суть новости (2-3 предложения).\n"
        f"3. Список ГЛАВНЫХ фактов (3-4 пункта, перед каждым ставь смайл: 🔥, 🚀, 📍, 💎).\n"
        f"4. Итог одним коротким законченным предложением.\n\n"
        f"ПРАВИЛА: Используй много смайликов. Пиши понятно. Не обрывай на полуслове!"
    )
    try:
        # Автоматический выбор модели и провайдера без лишних списков
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}]
        )
        res = response.strip()
        res = re.sub(r'\.{2,}|…$', '.', res) # Срезаем многоточия
        return res
    except:
        return f"<b>{title}</b>\n\n{content[:500]}."

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR хайп OR нейросети)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get('articles', [])
    except:
        return

    posted = get_posted_links()

    for art in articles:
        link = art['url']
        if link in posted: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 400) else art.get('description', "")
        
        if not content: continue

        final_post = rewrite_text(art['title'], content)
        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break
        except:
            continue

if __name__ == "__main__":
    run()
