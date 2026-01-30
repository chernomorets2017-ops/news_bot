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
        text = " ".join([p.get_text() for p in soup.find_all('p')])
        return text[:2500]
    except:
        return None

def rewrite_text(title, content):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OR_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemini-flash-1.5-exp",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"перескажи новость как настоящий редактор популярного тгк\n\n"
                    f"ЗАГОЛОВОК: {title}\n"
                    f"ДАННЫЕ: {content[:1800]}\n\n"
                    f"ФОРМАТ:\n"
                    f"1. Жирный заголовок с эмодзи в начале.\n"
                    f"2. Суть новости в 2-3 коротких абзацах.\n"
                    f"3. Список важных фактов через •.\n"
                    f"4. Вывод или совет в конце.\n"
                    f"5. Хайповые хештеги."
                )
            }
        ],
        "temperature": 0.8
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except:
        return f"🔥 <b>{title}</b>\n\n{content[:300]}..."

def run():
    q = "(YouTube OR TikTok OR VK OR блогер OR скандал OR ЧП OR инцидент OR новости OR политика)"
    url = f"https://newsapi.org/v2/everything?q={q}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
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
        
        final_post = rewrite_text(title, content)
        if not final_post or len(final_post) < 100: continue
        
        caption = f"{final_post}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        if len(caption) > 1024:
            caption = caption[:1020] + "..."
            
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
