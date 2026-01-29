import os
import sys

# Принудительная установка библиотек прямо в рантайме
def install_deps():
    os.system(f"{sys.executable} -m pip install duckduckgo_search pyTelegramBotAPI beautifulsoup4 requests")

try:
    from duckduckgo_search import DDGS
except ImportError:
    install_deps()
    from duckduckgo_search import DDGS

import telebot
import requests
import re
from bs4 import BeautifulSoup

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
    # Очищаем заголовок от лишнего мусора для точного сравнения
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
        f"Напиши пост для Telegram. СДЕЛАЙ ЕГО ПОЛНЫМ И ЗАКОНЧЕННЫМ.\n"
        f"НОВОСТЬ: {title}\n"
        f"ТЕКСТ: {content}\n\n"
        f"СТРОГИЕ ПРАВИЛА:\n"
        f"1. Начни с жирного заголовка и смайла. 🔥\n"
        f"2. Расскажи суть подробно (3-4 абзаца). БЕЗ ОБРЫВОВ.\n"
        f"3. Используй смайлы (⚡️, 🚀, 📍, 💎) для акцентов.\n"
        f"4. В конце — законченный вывод. НИКАКИХ МНОГОТОЧИЙ.\n"
        f"5. ЗАПРЕТ: Не пиши ссылки и названия сайтов."
    )
    try:
        with DDGS() as ddgs:
            results = ddgs.chat(prompt, model='gpt-4o-mini')
            # Если ИИ всё же бросил многоточие — меняем на точку
            res = results.strip()
            if res.endswith('...') or res.endswith('…'):
                res = res.rsplit(' ', 1)[0] + "."
            return res
    except:
        return f"<b>{title}</b>\n\n{content[:600]}."

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR хайп OR нейросети OR технологии)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get('articles', [])
    except:
        return

    posted_data = get_posted_data()

    for art in articles:
        link = art['url']
        title = art['title']
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        
        # Проверка: если ссылка ИЛИ похожий заголовок уже были — скипаем
        if link in posted_data or clean_title in posted_data:
            continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 400) else art.get('description', "")
        
        if not content or len(content) < 100: continue

        final_post = rewrite_text(title, content)
        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            
            save_posted_data(link, title)
            print(f"Опубликовано: {title}")
            break # Публикуем ОДНУ свежую новость за раз
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            continue

if __name__ == "__main__":
    run()
