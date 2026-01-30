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
        return text[:1500]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Ты — редактор новостей. Напиши пост для ТГ.\n\n"
        f"ТЕМА: {title}\n"
        f"ИНФО: {content[:1000]}\n\n"
        f"ФОРМАТ:\n"
        f"1. 🔥 **ЖИРНЫЙ ЗАГОЛОВОК**\n\n"
        f"2. Суть в 2 предложениях. ЗАКОНЧИ МЫСЛЬ ТОЧКОЙ.\n\n"
        f"3. 2 главных факта через буллит •\n\n"
        f"4. Итог одной фразой.\n\n"
        f"ВАЖНО: Пиши кратко (до 400 знаков). Если не влезаешь — просто закончи мысль точкой."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='gpt-4o-mini')
            res = response.strip()
            
            # Убираем системные фразы нейронки
            res = re.sub(r'^(Вот|Ваш|Пост|Пересказ).*?:', '', res, flags=re.IGNORECASE).strip()
            
            # Если текст оборван — режем до последней точки
            if res and res[-1] not in '.!?»':
                last_mark = max(res.rfind('.'), res.rfind('!'), res.rfind('?'))
                if last_mark != -1:
                    res = res[:last_mark + 1]
            return res
    except:
        return None

def run():
    # Прямой запрос по ключевым словам
    url = f"https://newsapi.org/v2/everything?q=технологии+OR+нейросети+OR+гаджеты&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url).json()
        articles = r.get('articles', [])
    except: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        if not title or link in posted_data: continue
        
        content = get_full_article(link) or art.get('description')
        if not content or len(content) < 150: continue

        final_post = rewrite_text(title, content)
        
        if not final_post or len(final_post) < 120: continue

        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break
        except: continue

if __name__ == "__main__":
    run()
