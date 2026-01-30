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
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']): s.decompose()
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:3800]
    except:
        return None

def rewrite_text(title, content):
    CORE_LOGIC = (
        f"Напиши хайповый пост для Telegram о событиях в соцсетях и мире.\n\n"
        f"ТЕМА: {title}\n"
        f"ДАННЫЕ: {content}\n\n"
        f"ИНСТРУКЦИЯ:\n"
        f"1. Сделай очень жирный и провокационный заголовок с эмодзи.\n"
        f"2. Подробно разбери ситуацию: что случилось в соцсетях (VK, YouTube, TikTok, Telegram), что говорят блогеры, какие скандалы или инсайды.\n"
        f"3. Если это ЧП, политика или погода — пиши жестко и по делу.\n"
        f"4. Пиши длинно (1500-2500 знаков), используй абзацы.\n"
        f"5. Никаких списков, только живой авторский текст.\n"
        f"6. Обязательно закончи мысль и добавь хайповые хештеги."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(CORE_LOGIC, model='gpt-4o-mini')
            text = response.strip()
            text = re.sub(r'^(Вот|Пост|Редактор|Новость).*?:\s*', '', text, flags=re.IGNORECASE | re.DOTALL)
            return text
    except:
        return None

def run():
    search_query = "(YouTube OR TikTok OR Instagram OR VK OR Telegram OR блогер OR скандал OR шоу-бизнес OR политика OR ЧП OR происшествие OR погода OR новости)"
    url = f"https://newsapi.org/v2/everything?q={search_query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    try:
        articles = requests.get(url).json().get('articles', [])
    except: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        
        if link in posted_data or clean_title in posted_data: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 300) else art.get('description', "")
        if not content: continue

        final_text = rewrite_text(title, content)
        if not final_text or len(final_text) < 300: continue

        full_message = f"{final_text}\n\n🗞 <b><a href='https://t.me/SUP_V_BotK'>Подписаться на SUP_V_BotK</a></b>"

        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'])
            
            bot.send_message(CHANNEL_ID, full_message, parse_mode='HTML', disable_web_page_preview=True)
            
            save_posted_data(link, title)
            break
        except: continue

if __name__ == "__main__":
    run()
