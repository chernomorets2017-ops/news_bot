import os
import telebot
import requests
import re
import random
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916" 
CHANNEL_ID = "@SUP_V_BotK"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_data():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

def save_posted_data(link, title):
    clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n{clean_title}\n")

def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']): s.decompose()
        text = " ".join([p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 40])
        return text[:2000]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Ты — редактор ТГ-канала. Сделай пост из этого текста.\n\n"
        f"НОВОСТЬ: {title}\n"
        f"ТЕКСТ: {content[:1500]}\n\n"
        f"ФОРМАТ:\n"
        f"1. ⚡️ ЖИРНЫЙ ЗАГОЛОВОК (суть одним предложением)\n\n"
        f"2. Коротко: что произошло (1-2 предложения).\n\n"
        f"3. Главные факты и цифры:\n"
        f"• факт 1\n"
        f"• факт 2\n\n"
        f"4. Итог: краткий вывод или что делать.\n\n"
        f"ЗАПРЕТ: Никакой воды, ссылок и вступлений. Текст до 400 знаков."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='gpt-4o-mini')
            res = response.strip()
            res = re.sub(r'^(Вот|Ваш|Пересказ|Пост).*?:', '', res, flags=re.IGNORECASE).strip()
            if res and res[-1] not in '.!?': res += '.'
            return res
    except:
        return None

def run():
    endpoints = [
        f"https://newsapi.org/v2/top-headlines?country=ru&apiKey={NEWS_API_KEY}",
        f"https://newsapi.org/v2/everything?q=(технологии OR нейросети OR выплаты OR законы)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    ]
    
    articles = []
    for url in endpoints:
        try:
            r = requests.get(url).json()
            if r.get('articles'):
                articles.extend(r['articles'])
        except: continue
        
    if not articles: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        if not title or link in posted_data: continue
        
        content = get_full_article(link) or art.get('description') or art.get('content')
        if not content or len(content) < 100: continue

        final_post = rewrite_text(title, content)
        if not final_post or len(final_post) < 120: continue

        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage') and requests.head(art['urlToImage']).status_code == 200:
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break
        except:
            bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break

if __name__ == "__main__":
    run()

