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
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:4000]
    except:
        return None

def get_news():
    query = "(Россия OR экономика OR celebrity OR нейросети OR ТикТок OR TikTok OR YouTube OR Twitch OR Instagram OR Reels OR блогеры OR хайп OR инфлюенсеры OR MrBeast OR Logan+Paul OR поп-культура)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get('articles', [])
    except:
        return []

def rewrite_text(title, full_content):
    prompt = (
        f"Ты топовый редактор медиа. Сделай подробный хайповый пересказ статьи.\n"
        f"ЗАГОЛОВОК: {title}\n"
        f"ТЕКСТ СТАТЬИ: {full_content}\n\n"
        f"ТРЕБОВАНИЯ:\n"
        f"1. Пиши дерзко, с иронией, используй сленг.\n"
        f"2. Раскрой детали новости максимально подробно.\n"
        f"3. Используй ОЧЕНЬ МНОГО тематических ЭМОДЗИ и символов.\n"
        f"4. Заголовок жирным КАПСОМ.\n"
        f"5. НЕ вставляй в текст сторонние ссылки.\n"
        f"Объем: 700-1000 знаков."
    )
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        clean_res = re.sub(r'http[s]?://\S+', '', response)
        return clean_res
    except:
        return f"<b>{title.upper()}</b>\n\n{full_content[:500]}..."

def run():
    posted_links = get_posted_links()
    articles = get_news()
    
    for art in articles:
        link = art['url']
        if link in posted_links: 
            continue
        
        full_content = get_full_article(link)
        if not full_content or len(full_content) < 300:
            full_content = art.get('description', "")

        if not full_content or len(full_content) < 10:
            continue

        text = rewrite_text(art['title'], full_content)
        img = art.get('urlToImage')
        
        caption = (
            f"{text}\n\n"
            f"📍 <a href='{link}'>ИСТОЧНИК</a>\n"
            f"🗞 <b>Читать в: <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        )
        
        try:
            if img:
                bot.send_photo(CHANNEL_ID, img, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            
            save_posted_link(link)
            break 
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
