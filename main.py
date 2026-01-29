import os
import telebot
import requests
import re
import random
from bs4 import BeautifulSoup
import g4f

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
        return text[:4000]
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"Напиши развернутый и яркий пост для ТГ. ТЕМА: {title}\n"
        f"ДАННЫЕ: {content}\n\n"
        f"СТРОЖАЙШИЙ РЕГЛАМЕНТ:\n"
        f"1. ⚡️ 🔥 **ЖИРНЫЙ ХАЙПОВЫЙ ЗАГОЛОВОК**.\n\n"
        f"2. ВВЕДЕНИЕ: Раскрой суть новости максимально подробно. Пиши 3-4 предложения.\n\n"
        f"3. РАЗБОР ПО ТЕЗИСАМ (Детально):\n"
        f"📍 ТЕЗИС 1: Раскрой первую важную деталь подробно.\n\n"
        f"🚀 ТЕЗИС 2: Раскрой вторую важную деталь подробно.\n\n"
        f"💎 ТЕЗИС 3: Раскрой третью важную деталь подробно.\n\n"
        f"4. ИТОГО: Яркое завершение мысли. Поставь жирную точку.\n\n"
        f"ЗАПРЕТЫ: НИКАКИХ ССЫЛОК. НИКАКИХ МНОГОТОЧИЙ. Каждая мысль должна быть закончена!"
    )
    try:
        # Используем Blackbox, он лучше всего держит структуру
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o,
            messages=[{"role": "user", "content": prompt}],
            provider=g4f.Provider.Blackbox
        )
        text = response.strip()
        
        # Если ИИ обрезал конец, находим последнюю точку
        last_mark = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
        if last_mark != -1:
            text = text[:last_mark + 1]
            
        return text
    except:
        return f"🔥 <b>{title}</b>\n\n{content[:500]}."

def run_autopost():
    url = f"https://newsapi.org/v2/everything?q=(IT OR технологии OR нейросети OR гаджеты)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
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
        content = raw_text if (raw_text and len(raw_text) > 400) else art.get('description', "")
        if not content: continue

        final_post = rewrite_text(title, content)
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
    run_autopost()
