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
        for s in soup(['script', 'style', 'nav', 'footer', 'header']): s.decompose()
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:5000]
    except:
        return None

def get_news():
    query = "(IT OR технологии OR гаджеты OR нейросети OR игры OR крипта OR шоубиз OR хайп OR блогеры OR мемы)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ru&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get('articles', [])
    except:
        return []

def rewrite_text(title, full_content):
    prompt = (
        f"Ты — креативный админ хайпового Telegram-канала. Напиши пост по статье.\n\n"
        f"ЗАГОЛОВОК: {title}\n"
        f"ТЕКСТ:\n{full_content}\n\n"
        f"ЗАДАЧА:\n"
        f"1. Сделай КРУТОЙ ЖИРНЫЙ ЗАГОЛОВОК.\n"
        f"2. Напиши подробный, сочный текст (800-1200 знаков). Не сокращай суть!\n"
        f"3. Используй абзацы и списки.\n"
        f"4. СТИКЕРЫ И ЭМОДЗИ: Добавляй их часто! Вставляй подходящие по смыслу эмодзи в начале строк и в конце абзацев. 🚀🔥💎\n"
        f"5. Стиль: молодежный, ироничный, экспертный.\n"
        f"6. В конце добавь призыв к обсуждению или дерзкий вопрос."
    )
    try:
        response = g4f.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return re.sub(r'http[s]?://\S+', '', response)
    except:
        return f"<b>{title.upper()}</b>\n\n{full_content[:500]}..."

def run():
    posted_links = get_posted_links()
    articles = get_news()
    if not articles: return

    for art in articles:
        link = art['url']
        if link in posted_links: continue
        
        full_content = get_full_article(link)
        if not full_content or len(full_content) < 400:
            full_content = art.get('description', "")

        if len(full_content) < 50: continue

        text = rewrite_text(art['title'], full_content)
        img = art.get('urlToImage')
        
        caption = f"{text}\n\n📍 <a href='{link}'>ИСТОЧНИК</a>\n🗞 <b>Подпишись на <a href='https://t.me/SUP_V_BotK'>SUP_V_BotK</a></b>"
        
        try:
            if img:
                bot.send_photo(CHANNEL_ID, img, caption=caption, parse_mode='HTML')
            else:
                bot.send_message(CHANNEL_ID, caption, parse_mode='HTML')
            save_posted_link(link)
            break 
        except:
            continue

if __name__ == "__main__":
    run()
