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
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']): s.decompose()
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
        return text[:3500] if text else None
    except:
        return None

def rewrite_text(title, content):
    prompt = (
        f"ИНСТРУКЦИЯ: Напиши полноценный, законченный новостной пост для Telegram. "
        f"Используй HTML-разметку (<b> и <i>).\n\n"
        f"СТРУКТУРА:\n"
        f"1. Жирный заголовок.\n"
        f"2. Суть события (2-3 подробных абзаца).\n"
        f"3. Список фактов через •.\n"
        f"4. Блок 'Итог'.\n"
        f"5. Хештеги.\n\n"
        f"ЗАПРЕТ: Не используй вводные фразы. Текст должен быть завершенным.\n\n"
        f"ЗАГОЛОВОК: {title}\n"
        f"ДАННЫЕ: {content[:2500]}"
    )
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(prompt, model='claude-3-haiku')
            if not response: return None
            text = response.strip()
            text = re.sub(r'^(Вот|Ваш|Держите|Готовый|Конечно|Редактор).*:(\s+)?', '', text, flags=re.IGNORECASE | re.MULTILINE)
            return text
    except:
        return None

def run():
    url = f"https://newsapi.org/v2/everything?q=(IT OR технологии OR нейросети OR гаджеты)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url)
        articles = res.json().get('articles', [])
    except: return

    if not articles: return

    posted_data = get_posted_data()
    random.shuffle(articles)

    for art in articles:
        link = art['url']
        title = art['title']
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        
        if link in posted_data or clean_title in posted_data: continue
        
        raw_text = get_full_article(link)
        content = raw_text if (raw_text and len(raw_text) > 400) else art.get('description', "")
        
        if not content or len(content) < 200: continue

        final_post = rewrite_text(title, content)
        
        if not final_post or len(final_post) < 400:
            continue

        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_data(link, title)
            break 
        except:
            continue

if __name__ == "__main__":
    run()
