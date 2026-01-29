import telebot
import requests
import os
import re
from bs4 import BeautifulSoup

# Устанавливаем спец. библиотеку для стабильного ИИ
os.system('pip install duckduckgo_search')
from duckduckgo_search import DDGS

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
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']): s.decompose()
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:3000]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Напиши пост для Телеграм на основе новости.\n"
        f"НОВОСТЬ: {title}\n"
        f"ТЕКСТ: {content}\n\n"
        f"ПРАВИЛА:\n"
        f"1. Сначала жирный заголовок с крутым смайлом. 🔥\n"
        f"2. Коротко суть (2-3 предложения).\n"
        f"3. Список фактов (3 пункта, перед каждым СВОЙ жирный смайл: ⚡️, 💎, 🚀).\n"
        f"4. Итог одним коротким предложением. БЕЗ МНОГОТОЧИЙ.\n"
        f"НИКАКИХ ссылок и упоминаний источников!"
    )
    try:
        # Используем DuckDuckGo AI (модель GPT-4o-mini) - она не обрывает текст
        with DDGS() as ddgs:
            results = ddgs.chat(prompt, model='gpt-4o-mini')
            res = results.strip()
            return re.sub(r'\.{2,}|…$', '.', res)
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
