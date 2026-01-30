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
        # Режем вход ОЧЕНЬ СИЛЬНО, чтобы ИИ не тупил
        return text[:800]
    except:
        return None

def rewrite_text(title, content):
    # Упрощаем промпт до уровня табуретки
    INSTRUCTION = (
        f"Напиши один большой связный абзац про эту новость: {title}\n\n"
        f"ИНФОРМАЦИЯ: {content}\n\n"
        f"ТРЕБОВАНИЯ:\n"
        f"1. Начни с жирного заголовка.\n"
        f"2. Пиши только текстом, без списков и точек.\n"
        f"3. В конце обязательно напиши 'Конец связи.'\n"
        f"4. Не обрывай на полуслове, закончи мысль."
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(INSTRUCTION, model='gpt-4o-mini')
            text = response.strip()
            
            # Убираем системный мусор
            text = re.sub(r'^(Вот|Пересказ|Редактор|Пост).*?:\s*', '', text, flags=re.IGNORECASE)
            
            # Если она написала 'Конец связи', значит она точно дошла до конца
            text = text.replace('Конец связи.', '').strip()
            return text
    except:
        return f"🔥 <b>{title}</b>\n\n{content[:400]}..."

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR технологии OR нейросети)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
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
        content = raw_text if (raw_text and len(raw_text) > 200) else art.get('description', "")
        if not content: continue

        final_post = rewrite_text(title, content)
        
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
        except: continue

if __name__ == "__main__":
    run()
