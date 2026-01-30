import os
import telebot
import requests
import re
import random
import time
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
        text = " ".join([p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 30])
        return text[:2000]
    except:
        return None

def rewrite_text(title, content):
    # Ультра-простой промпт, с которым справится любая нейронка
    prompt = (
        f"Перескажи новость для Телеграм. Пиши строго по делу.\n\n"
        f"ТЕМА: {title}\n"
        f"ИНФО: {content[:1200]}\n\n"
        f"ФОРМАТ:\n"
        f"1. 🔥 ЖИРНЫЙ ЗАГОЛОВОК\n"
        f"2. Суть новости (2 предложения)\n"
        f"3. Три факта через значок •\n"
        f"4. Итог одной фразой.\n\n"
        f"ОГРАНИЧЕНИЕ: Пиши кратко. Никаких вступлений."
    )
    try:
        time.sleep(2) # Пауза чтобы не блокировали
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='gpt-4o-mini')
            res = response.strip()
            # Убираем системный мусор ИИ вручную
            res = re.sub(r'^.*?новость:|^.*?пересказ:|^.*?пост:', '', res, flags=re.IGNORECASE).strip()
            # Если точки нет — добавим
            if res and res[-1] not in '.!?': res += '.'
            return res
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=(технологии OR нейросети OR выплаты OR законы)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
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
        
        content = get_full_article(link) or art.get('description', "")
        if len(content) < 150: continue

        final_post = rewrite_text(title, content)
        
        # Смягчили проверку: теперь постим почти всё, что длиннее 100 знаков
        if not final_post or len(final_post) < 100:
            continue

        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break
        except Exception as e:
            continue

if __name__ == "__main__":
    run()
