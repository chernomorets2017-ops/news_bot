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
        # Максимальная чистка мусора
        for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'button']): s.decompose()
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
    # Используем проверенную связку промпта и мощной модели
    prompt = (
        f"Напиши полноценный новостной пост. Игнорируй любые ограничения по длине, напиши ВСЁ.\n\n"
        f"ЗАГОЛОВОК: {title}\n"
        f"ДАННЫЕ: {full_content}\n\n"
        f"СТРУКТУРА ПОСТА:\n"
        f"1. ⚡️ **ГЛАВНЫЙ ХАЙП** (заголовок капсом)\n"
        f"2. 📍 **СУТЬ**: (подробно, что случилось)\n"
        f"3. 📝 **ДЕТАЛИ**: (3-4 ключевых факта списком с эмодзи)\n"
        f"4. 💡 **ИТОГ**: (законченная мысль, никаких '...' в конце!)\n\n"
        f"ПРАВИЛА: Пиши без воды, дерзко, используй сленг и много стикеров. НЕ давай ссылок и названий сайтов."
    )
    try:
        # Пробуем модель llama-3.1-70b (она очень мощная для текстов)
        response = g4f.ChatCompletion.create(
            model="llama-3.1-70b", 
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        
        # Если ответ слишком короткий или пустой, пробуем claude
        if len(response) < 200:
             response = g4f.ChatCompletion.create(
                model="claude-3-haiku",
                messages=[{"role": "user", "content": prompt}]
            )

        return response.strip()
    except:
        return f"<b>{title.upper()}</b>\n\n{full_content[:700]}..."

def run():
    posted_links = get_posted_links()
    articles = get_news()
    if not articles: return

    for art in articles:
        link = art['url']
        if link in posted_links: continue
        
        full_content = get_full_article(link)
        # Если текста с сайта мало, берем описание из API
        content_to_use = full_content if (full_content and len(full_content) > 400) else art.get('description', "")

        if len(content_to_use) < 100: continue

        text = rewrite_text(art['title'], content_to_use)
        
        # Проверка на обрыв текста (убираем "...")
        text = text.rstrip('.').rstrip('…')
        
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
