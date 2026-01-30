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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']): s.decompose()
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return " ".join(text.split())[:2000]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Ты — автор агрессивного новостного ТГ-канала о медиа, скандалах и политике.\n"
        f"ЗАДАЧА: Перескажи новость максимально хайпово и кратко.\n"
        f"НОВОСТЬ: {title} | {content[:1000]}\n\n"
        f"ФОРМАТ:\n"
        f"1. ⚡️ ЖИРНЫЙ КЛИКБЕЙТНЫЙ ЗАГОЛОВОК (суть шока)\n"
        f"2. Что произошло на самом деле (1-2 предложения, без воды)\n"
        f"3. Список 'Грязных подробностей' через буллиты •\n"
        f"4. Итог: Почему это важно или что будет дальше.\n"
        f"5. Хайповые хештеги.\n\n"
        f"БЕЗ ЛИШНИХ СЛОВ. Объем до 550 знаков. Только русский язык."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='gpt-4o-mini')
            if response:
                text = re.sub(r'(?i)^(Вот|Ваш|Текст|Пост).*:', '', response).strip()
                return text
            return None
    except:
        return None

def run():
    # Набор запросов: политика, скандалы, соцсети, западные звезды, сериалы, происшествия
    queries = [
        "скандал соцсети", "шоубизнес запад", "новости сериалов", 
        "политика происшествия", "TikTok тренды скандал", "YouTube блогеры новости",
        "Илон Маск скандал", "Netflix премьеры", "Голливуд сплетни"
    ]
    query = random.choice(queries)
    
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    try:
        resp = requests.get(url, timeout=10).json()
        articles = resp.get('articles', [])
    except: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        if not title or len(title) < 10: continue
        
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        if link in posted_data or clean_title in posted_data: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 300) else art.get('description', "")
        if not content: continue

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
