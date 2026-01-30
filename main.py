import os
import telebot
import requests
import re
import random
from bs4 import BeautifulSoup

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916"
HF_TOKEN = "Hf_WbClEYUXXnScbaydWjQlTtwbROQJQtVrMi"
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
        return text[:1500]
    except:
        return None

def rewrite_text(title, content):
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"Ты — редактор популярного телеграм-канала. Твоя задача: пересказать новость хайпово, кратко и с эмодзи. <|eot_id|>\n"
        f"<|start_header_id|>user<|end_header_id|>\n"
        f"Вот новость: {title}. {content[:1200]}\n\n"
        f"ТВОЯ ЗАДАЧА: перескажи новость как настоящий редактор популярного тгк <|eot_id|>\n"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
    )
    
    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 450,
                "temperature": 0.6,
                "top_p": 0.9,
                "return_full_text": False
            }
        }, timeout=20)
        
        result = response.json()
        if isinstance(result, list):
            text = result[0]['generated_text'].strip()
        else:
            text = result['generated_text'].strip()
            
        text = re.sub(r'<\|.*?\|>', '', text)
        return text
    except:
        return None

def run():
    q = "(YouTube OR TikTok OR скандал OR ЧП OR блогер OR инцидент OR новости OR криминал OR политика)"
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
        content = raw_text if (raw_text and len(raw_text) > 200) else art.get('description', "")
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
