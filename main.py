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
        # Вырезаем мусор, чтобы нейронка не путалась
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']): s.decompose()
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs])
        return full_text[:5000]
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
    # Используем модель gpt-4o для лучшего качества
    prompt = (
        f"Ты — профессиональный автор контента. Твоя задача написать ПОЛНЫЙ и ЗАВЕРШЕННЫЙ пост.\n\n"
        f"ТЕМА: {title}\n"
        f"ДАННЫЕ: {full_content}\n\n"
        f"ПЛАН ПОСТА:\n"
        f"1. 🔥 ЖИРНЫЙ ЗАГОЛОВОК КАПСОМ.\n"
        f"2. ⚡️ ЧТО ПРОИЗОШЛО: (внятное вступление на 2-3 предложения).\n"
        f"3. 🔍 ГЛАВНЫЕ ФАКТЫ: (структурированный список с эмодзи-маркерами).\n"
        f"4. 💎 ИТОГ: (финальный вывод, мысль должна быть закончена).\n\n"
        f"ВАЖНО:\n"
        f"- ПИШИ ДО КОНЦА. Если текст прервется, пост будет удален.\n"
        f"- Не используй ссылки и не упоминай названия сторонних сайтов.\n"
        f"- Используй много стикеров и эмодзи.\n"
        f"- Стиль: хайповый, без лишней воды."
    )
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o", # СМЕНИЛИ МОДЕЛЬ ЗДЕСЬ
            messages=[{"role": "user", "content": prompt}],
            timeout=40
        )
        # Убираем возможные системные приписки
        clean_res = re.sub(r'http[s]?://\S+', '', response)
        return clean_res.strip()
    except Exception as e:
        print(f"Ошибка нейронки: {e}")
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
            print(f"Ошибка Telegram: {e}")
            continue

if __name__ == "__main__":
    run()
