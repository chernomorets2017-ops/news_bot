import os
import telebot
import requests
import re
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
OR_TOKEN = "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"
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
        return " ".join([p.get_text() for p in soup.find_all('p')])[:2000]
    except:
        return None

def rewrite_text(title, content):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OR_TOKEN}", "Content-Type": "application/json"}
    
    instruction = (
        f"Новость: {title}\n"
        f"Текст: {content[:1500]}\n\n"
        f"Сделай готовый пост:\n"
        f"1. Заголовок с эмодзи\n"
        f"2. Суть в 2 абзаца своими словами\n"
        f"3. Три главных факта через •\n"
        f"4. Вопрос читателям\n"
        f"5. 3 хештега"
    )
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": "google/gemini-flash-1.5",
            "messages": [{"role": "user", "content": instruction}],
            "temperature": 0.8
        }, timeout=25)
        return response.json()['choices'][0]['message']['content'].strip()
    except:
        return None

def run():
    api_url = f"https://newsapi.org/v2/everything?q=(блогер OR скандал OR ЧП OR новости OR инцидент)&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(api_url)
        articles = r.json().get('articles', [])
    except: return
    
    posted_data = get_posted_data()
    random.shuffle(articles)
    
    for art in articles:
        link, title = art['url'], art['title']
        clean_title = re.sub(r'[^\w\s]', '', title).lower().strip()
        if link in posted_data or clean_title in posted_data: continue
        
        content = get_full_article(link) or art.get('description', "")
        if not content or len(content) < 150: continue
        
        final_post = rewrite_text(title, content)
        if not final_post: continue
        
        full_text = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if art.get('urlToImage'):
                bot.send_photo(CHANNEL_ID, art['urlToImage'], caption=full_text[:1024], parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, full_text, parse_mode='HTML')
            save_posted_data(link, title)
            break
        except: continue

if __name__ == "__main__":
    run()
