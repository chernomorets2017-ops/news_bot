import telebot
import g4f
import requests
import os
import re
from bs4 import BeautifulSoup

BOT_TOKEN = "8546746980:AAF3z5K85WaBMC-SKTSTN5Tx_dXxXyZXIoQ"
NEWS_API_KEY = "E16b35592a2147989d80d46457d4f916" 
CHANNEL_ID = "@SUP_V_BotK"
DB_FILE = "last_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def get_posted_links():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_posted_link(link):
    with open(DB_FILE, "a") as f: f.write(link + "\n")

def get_full_article(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']): s.decompose()
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:4500]
    except:
        return None

def get_news():
    query = "(IT OR технологии OR нейросети OR гаджеты OR игры OR крипта OR шоубиз OR хайп OR блогеры)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get('articles', [])
    except:
        return []

def rewrite_text(title, full_content):
    prompt = (
        f"Напиши новостной пост в стиле топовых ТГ-каналов (типа ВПШ или ТОПОР).\n\n"
        f"ЗАГОЛОВОК СТАТЬИ: {title}\n"
        f"ТЕКСТ: {full_content}\n\n"
        f"ФОРМАТ:\n"
        f"1. СУПЕР-ХАЙПОВЫЙ ЗАГОЛОВОК (жирный капс + эмодзи) 🔥\n\n"
        f"2. ПЕРВЫЙ АБЗАЦ: Суть новости в 2 предложениях. Максимально вовлекающе. ⚡️\n\n"
        f"3. ДЕТАЛИ: Список из 3-5 пунктов через тире или крутые эмодзи-маркеры. Опиши самое важное и сочное. 🔍\n\n"
        f"4. ИТОГО: Финальный аккорд. Мысль должна быть закончена полностью. Никаких обрывов! 💎\n\n"
        f"ПРАВИЛА:\n"
        f"- ПИШИ ПОЛНОСТЬЮ. Не заканчивай текст фразами 'читайте далее' или многоточием.\n"
        f"- НЕ упоминай источник. Вообще. Совсем.\n"
        f"- Используй много тематических эмодзи.\n"
        f"- Объем: около 1000-1200 знаков."
    )
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=45
        )
        return response.strip()
    except:
        return f"<b>{title.upper()}</b>\n\n{full_content[:600]}..."

def run():
    posted_links = get_posted_links()
    articles = get_news()
    if not articles: return

    for art in articles:
        link = art['url']
        if link in posted_links: continue
        
        full_content = get_full_article(link)
        if not full_content or len(full_content) < 300:
            full_content = art.get('description', "")

        if len(full_content) < 100: continue

        text = rewrite_text(art['title'], full_content)
        img = art.get('urlToImage')
        
        caption = f"{text}\n\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if img:
                bot.send_photo(CHANNEL_ID, img, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break 
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    run()
